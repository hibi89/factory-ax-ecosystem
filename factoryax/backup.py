"""Manual local report backup/restore, new-only, no source data, no network.

A hash is an integrity check, NOT an authenticated signature.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED, BadZipFile

from .delivery import ARTIFACTS, COMPLETE, RECEIPT, verify_candidate, _sha
from .verify import IntakeError

BACKUP_FILES = tuple(sorted(set(ARTIFACTS) | {RECEIPT, COMPLETE}))
BACKUP_META = 'BACKUP_MANIFEST.json'


def backup(report_dir: str | Path, archive_path: str | Path) -> dict:
    report_dir = Path(report_dir)
    verify_candidate(report_dir)
    target = Path(archive_path).absolute()
    if target.suffix.lower() != '.zip' or not target.parent.is_dir() or target.parent.is_symlink() or target.exists() or target.is_symlink():
        raise IntakeError('BACKUP_TARGET_UNSAFE_OR_EXISTS')
    payloads = {name: (report_dir / name).read_bytes() for name in BACKUP_FILES}
    meta = {'schema': 'factoryax.report.backup.v1', 'release': 'HOLD',
            'sha256': {name: _sha(data) for name, data in payloads.items()},
            'authorization': 'OWNER_MANUAL_ONLY', 'signature': 'UNSIGNED'}
    payloads[BACKUP_META] = (json.dumps(meta, sort_keys=True, indent=2) + '\n').encode('utf-8')
    try:
        with target.open('xb') as output:
            with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
                for name, data in sorted(payloads.items()):
                    info = ZipInfo(name, (2024, 1, 1, 0, 0, 0))
                    info.compress_type = ZIP_DEFLATED
                    archive.writestr(info, data)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return {'status': 'BACKUP_CREATED', 'sha256': _sha(target.read_bytes()), 'release': 'HOLD'}


def restore(archive_path: str | Path, new_dir: str | Path) -> dict:
    archive_path = Path(archive_path)
    target = Path(new_dir).absolute()
    if archive_path.is_symlink() or not archive_path.is_file() or archive_path.stat().st_size > 20*1024*1024:
        raise IntakeError('BACKUP_SOURCE_UNSAFE_OR_TOO_LARGE')
    if (not target.parent.is_dir() or target.parent.is_symlink() or
            target.exists() or target.is_symlink()):
        raise IntakeError('RESTORE_TARGET_UNSAFE_OR_EXISTS')
    try:
        with ZipFile(archive_path, 'r') as archive:
            infos = archive.infolist()
            if (len(infos) != len(set(x.filename for x in infos)) or
                    set(x.filename for x in infos) != set(BACKUP_FILES) | {BACKUP_META} or
                    any(i.file_size > 10*1024*1024 or i.flag_bits & 1 or i.is_dir() or
                        (i.compress_size and i.file_size > i.compress_size*200) for i in infos)):
                raise IntakeError('BACKUP_UNSAFE_ENTRIES')
            data = {i.filename: archive.read(i) for i in infos}
        meta = json.loads(data[BACKUP_META])
    except (BadZipFile, OSError, ValueError, KeyError) as exc:
        if isinstance(exc, IntakeError):
            raise
        raise IntakeError('BACKUP_INVALID') from exc
    if (not isinstance(meta, dict) or meta.get('schema') != 'factoryax.report.backup.v1' or
            meta.get('release') != 'HOLD' or set(meta.get('sha256', {})) != set(BACKUP_FILES) or
            any(_sha(data[name]) != meta['sha256'][name] for name in BACKUP_FILES)):
        raise IntakeError('BACKUP_INTEGRITY_INVALID')
    # This is an owner-requested new location; source archive/report never modified.
    try:
        target.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise IntakeError('RESTORE_TARGET_UNSAFE_OR_EXISTS') from exc
    try:
        for name in BACKUP_FILES:
            with (target / name).open('xb') as stream:
                stream.write(data[name])
                stream.flush()
                os.fsync(stream.fileno())
        check = verify_candidate(target)
    except BaseException:
        try:
            (target / 'INCOMPLETE.txt').write_text('복구 검증 실패. 사용 금지.\n', encoding='utf-8')
        except OSError:
            pass
        raise
    return {'status': 'RESTORED_AND_VERIFIED', 'sha256': _sha(archive_path.read_bytes()),
            'report': check, 'release': 'HOLD'}
