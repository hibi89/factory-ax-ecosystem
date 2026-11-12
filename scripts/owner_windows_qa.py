"""Owner-only Windows 10/11 offline synthetic native acceptance runner.

No telemetry, customer paths, shell execution, installation, admin elevation or API.
Human must review generated local-only summary before sharing it.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / 'QA_SOURCE_MANIFEST.json'
TEST_FILES = ('test_verify.py','test_reconciliation.py','test_delivery.py','test_backup.py',
              'test_profile_contract.py','test_malformed_rejection.py','test_owner_windows_qa.py')
STEPS = ('source_manifest', 'compile', *(f'regression_{f[:-3]}' for f in TEST_FILES), 'synthetic', 'report',
         'report_verify', 'backup', 'restore', 'restore_verify', 'package',
         'package_verify', 'native_cmd_ok', 'native_cmd_blocked',
         'original_input_unchanged', 'native_tk_gui')


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_source_bundle() -> None:
    """Detect accidental transfer drift. Unsigned hashes are not authentication."""
    data = json.loads(SOURCE_MANIFEST.read_text(encoding='utf-8'))
    if data.get('schema') != 'factoryax.owner-qa-source.v1' or data.get('release') != 'HOLD':
        raise ValueError('SOURCE_MANIFEST_SCHEMA')
    files = data.get('files')
    if not isinstance(files, dict) or len(files) < 12:
        raise ValueError('SOURCE_MANIFEST_FILES')
    for name, expected in files.items():
        if (not isinstance(name, str) or not isinstance(expected, str) or
                re.fullmatch(r'[0-9a-f]{64}', expected) is None):
            raise ValueError('SOURCE_MANIFEST_ENTRY')
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name:
            raise ValueError('SOURCE_MANIFEST_PATH')
        candidate = ROOT / rel
        if candidate.is_symlink() or not candidate.is_file() or _sha(candidate) != expected:
            raise ValueError('SOURCE_MANIFEST_DRIFT')


def check_run(argv: list[str], name: str, checks: list[dict], *, expected: int = 0,
              timeout: int = 240) -> str:
    start = time.monotonic()
    try:
        run = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                             encoding='utf-8', errors='replace', timeout=timeout,
                             env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    except (OSError, subprocess.TimeoutExpired) as exc:
        checks.append({'step': name, 'status': 'FAIL', 'reason': type(exc).__name__})
        raise RuntimeError('STEP_LAUNCH_OR_TIMEOUT:'+name) from exc
    rec = {'step': name, 'status': 'PASS' if run.returncode == expected else 'FAIL',
           'exit_code': run.returncode, 'expected_exit_code': expected,
           'elapsed_seconds': round(time.monotonic()-start, 2)}
    if name.startswith('regression_'):
        m = re.search(r'Ran (\d+) tests?', run.stdout+'\n'+run.stderr)
        if m:
            rec['tests_run'] = int(m.group(1))
    checks.append(rec)
    print(name, rec['status'], 'exit', run.returncode, flush=True)
    if run.returncode != expected:
        # Do not embed captured Python tracebacks with temp file/user paths in summary.
        raise RuntimeError('STEP_EXIT_MISMATCH:'+name)
    return run.stdout+'\n'+run.stderr


def native_qa() -> tuple[int, dict]:
    summary = {'schema': 'factoryax.owner-windows-qa.v1',
               'generated_utc': datetime.now(timezone.utc).isoformat(),
               'windows_native': os.name == 'nt',
               'python_version': '.'.join(map(str,sys.version_info[:3])),
               'release': 'HOLD', 'source_manifest_signed': False,
               'status': 'NOT_RUN', 'steps': []}
    checks = summary['steps']
    if os.name != 'nt':
        summary['status'] = 'BLOCKED'
        summary['reason'] = 'NATIVE_WINDOWS_REQUIRED'
        return 3, summary
    if sys.version_info < (3, 11):
        summary['status'] = 'BLOCKED'
        summary['reason'] = 'PYTHON_3_11_REQUIRED'
        return 3, summary
    try:
        verify_source_bundle()
        checks.append({'step': 'source_manifest', 'status': 'PASS'})
        with tempfile.TemporaryDirectory(prefix='FactoryAX-Windows-NativeQA-') as temp:
            work = Path(temp)
            demo = work / '한글_합성_입력'
            report = work / '한글_검수_보고서'
            backup = work / '한글_백업.zip'
            restored = work / '한글_복원_보고서'
            package = work / '한글_검수_패키지'
            py = sys.executable
            check_run([py,'-m','compileall','-q','factoryax','tests','scripts','examples'], 'compile', checks)
            for test_file in TEST_FILES:
                check_run([py,'-m','unittest','discover','-s','tests','-p',test_file,'-q'],
                          'regression_'+test_file[:-3], checks, timeout=90)
            check_run([py,str(ROOT/'examples/make_reconcile_synthetic.py'),str(demo)], 'synthetic', checks)
            original={str(p.relative_to(demo)): _sha(p) for p in (demo/'input').iterdir() if p.is_file()}
            if len(original) != 4:
                raise ValueError('EXPECTED_FOUR_SYNTHETIC_INPUTS')
            check_run([py,'-m','factoryax','--spec',str(demo/'approved.json'),'--output',str(report)], 'report', checks)
            check_run([py,'-m','factoryax','--verify-report',str(report)], 'report_verify', checks)
            check_run([py,'-m','factoryax','--backup-report',str(report),'--output',str(backup)], 'backup', checks)
            check_run([py,'-m','factoryax','--restore-backup',str(backup),'--output',str(restored)], 'restore', checks)
            check_run([py,'-m','factoryax','--verify-report',str(restored)], 'restore_verify', checks)
            check_run([py,str(ROOT/'scripts/build_candidate.py'),'--output',str(package)], 'package', checks)
            check_run([py,str(ROOT/'scripts/build_candidate.py'),'--output',str(package),'--verify'], 'package_verify', checks)
            cmd = package / 'RUN_VERIFY_WINDOWS.cmd'
            check_run([str(cmd),'--verify-report',str(restored)], 'native_cmd_ok', checks)
            hash_before=_sha(report/'result.json')
            check_run([str(cmd),'--spec',str(demo/'approved.json'),'--output',str(report)], 'native_cmd_blocked', checks,expected=3)
            if _sha(report/'result.json') != hash_before:
                raise ValueError('BLOCKED_RUN_ALTERED_RESULT')
            if original != {str(p.relative_to(demo)): _sha(p) for p in (demo/'input').iterdir() if p.is_file()}:
                raise ValueError('INPUT_DRIFT')
            checks.append({'step':'original_input_unchanged','status':'PASS'})
            check_run([py,str(ROOT/'scripts/gui_smoke.py')], 'native_tk_gui', checks)
        summary['status']='SYNTHETIC_WINDOWS_PASS'
        summary['disclaimer']='Not customer, NTFS hostile race, antivirus, signature or commercial acceptance.'
        return 0, summary
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        summary['status']='FAIL'
        summary['reason']=str(exc) if str(exc).isupper() or str(exc).startswith('STEP_') else type(exc).__name__
        return 3, summary


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description='Factory AX owner-only native Windows QA, synthetic data only')
    parser.add_argument('--plan',action='store_true',help='Show planned steps without execution')
    args=parser.parse_args(argv)
    if args.plan:
        print(json.dumps({'schema':'factoryax.owner-windows-plan.v1','native_windows_required':True,
                          'steps':STEPS,'release':'HOLD'},ensure_ascii=False,indent=2))
        return 0
    rc,summary=native_qa()
    # Save only sanitized event/exit-code evidence. Never upload raw customer data or temp paths.
    path=Path(tempfile.gettempdir()) / ('FactoryAX_NATIVE_QA_'+uuid.uuid4().hex[:10]+'.json')
    try:
        path.write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        print('RESULT_FILE:',path,flush=True)
    except OSError:
        print('WARNING: RESULT_FILE_SAVE_FAILED',flush=True)
        print(json.dumps(summary,ensure_ascii=False),flush=True)
    print('QA_RESULT:',summary['status'],'REASON:',summary.get('reason','none'),'RELEASE: HOLD',flush=True)
    return rc


if __name__=='__main__':
    raise SystemExit(main())
