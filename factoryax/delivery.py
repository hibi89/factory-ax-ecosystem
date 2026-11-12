"""Local-only, fail-closed W1 VERIFY owner candidate delivery protocol.

Integrity receipts are *not* signatures or proofs of operator authorization.
The customer-facing output remains RELEASE HOLD until Windows/user acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from .verify import (IntakeError, ROLES, _read_exact, _safe_path, export_new,
                     verify)

ARTIFACTS = ('result.json', 'summary.csv', 'summary.html')
RECEIPT = 'receipt.json'
COMPLETE = 'COMPLETE.sha256'
SCHEMA = 'factoryax.verify.delivery.v1'


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_recheck(spec: dict, report: dict) -> None:
    """Detect sequential source changes, including after the last role was read.

    This cannot make four independent customer files a single atomic snapshot.
    """
    manifest = {s['role']: s for s in report['manifests']}
    for role in ROLES:
        pinned = spec['files'][role]
        path = _safe_path(spec['approved_root'], pinned['path'])
        contents, sha = _read_exact(path, pinned['sha256'])
        if sha != manifest[role]['sha256'] or len(contents) != manifest[role]['bytes']:
            raise IntakeError('SOURCE_DRIFT_BEFORE_REPORT_COMMIT')


def _require_plain_directory(directory: str | Path) -> Path:
    """Conservatively reject symlinks/junctions in *every* directory ancestor.

    This is a bounded preflight, not race-proof ACL enforcement: a privileged
    concurrent process can still replace a directory after checking it.
    """
    directory = Path(directory).absolute()
    for component in reversed((directory, *directory.parents)):
        try:
            info = component.lstat()  # unlike stat(), does not follow the link
        except OSError as exc:
            raise IntakeError('UNSAFE_DIRECTORY_ANCESTOR') from exc
        if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or
                getattr(info, 'st_file_attributes', 0) &
                getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
            raise IntakeError('UNSAFE_DIRECTORY_ANCESTOR')
    return directory


def _check_output_parent(out: Path) -> None:
    if not out.is_absolute() or out.name in ('', '.', '..'):
        raise IntakeError('OUTPUT_INVALID')
    _require_plain_directory(out.parent)
    if out.is_symlink() or out.exists() or os.path.lexists(out):
        raise IntakeError('OUTPUT_EXISTS_NO_OVERWRITE')


def _fsync_dir(directory: Path) -> None:
    if os.name != 'posix':
        return
    try:
        fd = os.open(directory, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        # Filesystem support varies; native Windows durable-commit unverified.
        pass


def export_candidate(report: dict, out: str | Path, *, spec: dict | None = None) -> None:
    """Reserve destination atomically, complete receipt last; never overwrite.

    A crash can leave an incomplete directory, which verify_candidate rejects.
    A competing hostile OS process/ACL is out of scope without native tests.
    """
    out = Path(out).absolute()
    _check_output_parent(out)
    scratch = Path(tempfile.mkdtemp(prefix='.fax-owner-stage-', dir=out.parent))
    reserved = False
    try:
        prepared = scratch / 'prepared'
        export_new(report, prepared)
        hashes = {name: _sha((prepared / name).read_bytes()) for name in ARTIFACTS}
        receipt = {'schema_version': SCHEMA, 'sha256': hashes,
                   'source_manifest_sha256': _sha(json.dumps(report['manifests'], sort_keys=True).encode()),
                   'status': report['status'], 'scope': report['scope'],
                   'authenticity': 'UNSIGNED_LOCAL_INTEGRITY_ONLY', 'release': 'HOLD'}
        receipt_data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
        (scratch / RECEIPT).write_bytes(receipt_data)
        complete_digest = _sha(receipt_data)
        (scratch / COMPLETE).write_text(complete_digest + '\n', encoding='ascii')
        for f in (scratch / RECEIPT, scratch / COMPLETE):
            with f.open('rb') as stream:
                os.fsync(stream.fileno())
        if spec is not None:
            _source_recheck(spec, report)
        # Atomic exclusive reservation even if an unrelated process wins the path race.
        try:
            out.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise IntakeError('OUTPUT_EXISTS_NO_OVERWRITE') from exc
        reserved = True
        for name in ARTIFACTS:
            os.replace(prepared / name, out / name)
        os.replace(scratch / RECEIPT, out / RECEIPT)
        _fsync_dir(out)
        os.replace(scratch / COMPLETE, out / COMPLETE)  # committed last
        _fsync_dir(out)
        _fsync_dir(out.parent)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        # On failure leave reservation as INCOMPLETE to prohibit accidental use.
        if reserved and not (out / COMPLETE).is_file():
            try:
                (out / 'INCOMPLETE.txt').write_text('검수 실패/중단. 이 폴더의 결과를 사용하지 마세요.\n', encoding='utf-8')
            except OSError:
                pass


def verify_candidate(out: str | Path) -> dict:
    out = _require_plain_directory(out)
    entries = {p.name for p in out.iterdir()}
    if entries != set(ARTIFACTS) | {RECEIPT, COMPLETE}:
        raise IntakeError('REPORT_UNEXPECTED_OR_MISSING_FILES')
    if any((out / name).is_symlink() or not (out / name).is_file() for name in entries):
        raise IntakeError('REPORT_UNSAFE_ENTRY')
    raw = (out / RECEIPT).read_bytes()
    complete = (out / COMPLETE).read_text(encoding='ascii')
    if complete != _sha(raw) + '\n':
        raise IntakeError('REPORT_RECEIPT_DRIFT')
    try:
        receipt = json.loads(raw)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise IntakeError('REPORT_INVALID_JSON') from exc
    if (not isinstance(receipt, dict) or receipt.get('schema_version') != SCHEMA or
        not isinstance(receipt.get('sha256'), dict) or
        set(receipt['sha256']) != set(ARTIFACTS) or
        any(not isinstance(receipt['sha256'][name], str) for name in ARTIFACTS) or
        receipt.get('release') != 'HOLD'):
        raise IntakeError('REPORT_RECEIPT_INVALID')
    for name in ARTIFACTS:
        if _sha((out / name).read_bytes()) != receipt['sha256'][name]:
            raise IntakeError('REPORT_FILE_DRIFT')
    try:
        report = json.loads((out / 'result.json').read_text(encoding='utf-8'))
    except (UnicodeError, ValueError, TypeError) as exc:
        raise IntakeError('REPORT_INVALID_JSON') from exc
    if (not isinstance(report, dict) or report.get('status') not in ('OK', 'REVIEW_REQUIRED') or
            not isinstance(report.get('manifests'), list) or
            receipt.get('status') != report['status'] or
            receipt.get('source_manifest_sha256') != _sha(json.dumps(report['manifests'], sort_keys=True).encode())):
        raise IntakeError('REPORT_RECEIPT_INVALID')
    return {'status': report['status'], 'receipt_sha256': _sha(raw),
            'files': len(ARTIFACTS), 'authenticity': 'UNSIGNED', 'release': 'HOLD'}


def run(spec_path: str | Path, output: str | Path) -> dict:
    source = Path(spec_path)
    _require_plain_directory(source.absolute().parent)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 1024 * 1024:
        raise IntakeError('SPEC_NOT_REGULAR_OR_TOO_LARGE')
    spec_bytes = source.read_bytes()
    try:
        spec = json.loads(spec_bytes)
    except (UnicodeError, ValueError) as exc:
        raise IntakeError('SPEC_INVALID_JSON') from exc
    # Validate the user-supplied JSON object before any path manipulation.
    if not isinstance(spec, dict) or not isinstance(spec.get('approved_root'), str):
        raise IntakeError('SPEC_SCHEMA_INVALID')
    # Output is always derived; do not create new directories inside input root.
    _require_plain_directory(spec['approved_root'])
    approved_root = Path(spec['approved_root']).resolve(strict=True)
    _require_plain_directory(Path(output).absolute().parent)
    out_parent = Path(output).absolute().parent.resolve(strict=True)
    if os.path.commonpath((str(approved_root), str(out_parent))) == str(approved_root):
        raise IntakeError('OUTPUT_INSIDE_APPROVED_INPUT_ROOT')
    report = verify(spec)
    if source.read_bytes() != spec_bytes:
        raise IntakeError('SPEC_CHANGED')
    export_candidate(report, output, spec=spec)
    verify_candidate(output)
    return {'status': report['status'], 'findings': len(report['findings']),
            'output': str(Path(output).absolute()), 'release': 'HOLD'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Factory AX VERIFY - offline restricted candidate, RELEASE HOLD')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--verify-report', help='Verify existing local output hashes')
    mode.add_argument('--gui', action='store_true', help='Local Tkinter preview (not yet Windows accepted)')
    mode.add_argument('--backup-report', help='Owner manual backup of an existing verified report')
    mode.add_argument('--restore-backup', help='Owner manual restore of an internal report backup')
    parser.add_argument('--spec', help='Explicit local spec JSON')
    parser.add_argument('--output', help='New, never previously created output directory')
    args = parser.parse_args(argv)
    try:
        if args.gui:
            from .gui import launch
            launch()
            return 0
        if args.verify_report:
            result = verify_candidate(args.verify_report)
        elif args.backup_report:
            if not args.output:
                parser.error('--backup-report requires --output NEW.zip')
            from .backup import backup
            result = backup(args.backup_report, args.output)
        elif args.restore_backup:
            if not args.output:
                parser.error('--restore-backup requires --output NEW_DIRECTORY')
            from .backup import restore
            result = restore(args.restore_backup, args.output)
        else:
            if not args.spec or not args.output:
                parser.error('--spec and --output are required')
            result = run(args.spec, args.output)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2 if result['status'] == 'REVIEW_REQUIRED' else 0
    except (IntakeError, OSError, ValueError, TypeError, KeyError) as exc:
        reason = str(exc) if isinstance(exc, IntakeError) else 'INVALID_LOCAL_INPUT_OR_IO'
        print(json.dumps({'status': 'BLOCKED', 'reason': reason, 'release': 'HOLD'}))
        return 3
