"""Build reproducible unsigned Python zipapp/Windows CMD QA bundle, no network."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import zipfile

FILES = ('factoryax/__init__.py', 'factoryax/__main__.py', 'factoryax/verify.py',
         'factoryax/reconcile.py', 'factoryax/delivery.py', 'factoryax/gui.py', 'factoryax/backup.py')
MAIN = "from factoryax.delivery import main\nraise SystemExit(main())\n"
LAUNCHER = ("@echo off\r\nsetlocal\r\n"
            "where py >nul 2>nul\r\n"
            "if errorlevel 1 goto use_python\r\n"
            "py -3 \"%~dp0FactoryAX-VERIFY.pyz\" %*\r\n"
            "exit /b %errorlevel%\r\n"
            ":use_python\r\n"
            "python \"%~dp0FactoryAX-VERIFY.pyz\" %*\r\n"
            "exit /b %errorlevel%\r\n")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(root: Path, dest: Path) -> dict:
    root = root.resolve(strict=True)
    if dest.exists() or dest.is_symlink():
        raise ValueError('OUTPUT_EXISTS_NO_OVERWRITE')
    if not dest.parent.is_dir() or dest.parent.is_symlink():
        raise ValueError('OUTPUT_PARENT_INVALID')
    contents = {}
    for name in FILES:
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('SOURCE_MISSING_OR_SYMLINK')
        contents[name] = path.read_bytes()
        if len(contents[name]) > 300000:
            raise ValueError('SOURCE_TOO_LARGE')
    # All files read prior to exclusive destination reservation.
    dest.mkdir(mode=0o700)
    target = dest / 'FactoryAX-VERIFY.pyz'
    with zipfile.ZipFile(target, 'w') as archive:
        for name, data in sorted({**contents, '__main__.py': MAIN.encode()}.items()):
            info = zipfile.ZipInfo(name, (2024, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    (dest / 'RUN_VERIFY_WINDOWS.cmd').write_bytes(LAUNCHER.encode('ascii'))
    (dest / 'README_QA.txt').write_text(
        'Factory AX VERIFY internal unsigned QA candidate / RELEASE HOLD\n'
        'Requires a separately installed Python 3.11+; no runtime bundled.\n'
        'RUN_VERIFY_WINDOWS.cmd --spec <approved.json> --output <new_dir>\n'
        'RUN_VERIFY_WINDOWS.cmd --verify-report <report_dir>\n'
        'RUN_VERIFY_WINDOWS.cmd --gui (Tkinter must be available)\n'
        'No customer deployment, security certification or native Windows test claimed.\n', encoding='utf-8')
    files = {p.name: sha(p.read_bytes()) for p in dest.iterdir() if p.is_file()}
    manifest = {'schema': 'factoryax.bundle.v1', 'release': 'HOLD',
                'signature': 'UNSIGNED', 'files': files,
                'zip_member_sha256': {name: sha(data) for name, data in contents.items()}}
    (dest / 'QA_MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    return manifest


def validate(dest: Path) -> dict:
    if dest.is_symlink() or not dest.is_dir():
        raise ValueError('PACKAGE_DIR_INVALID')
    manifest = json.loads((dest / 'QA_MANIFEST.json').read_text(encoding='utf-8'))
    files = manifest.get('files', {})
    if (manifest.get('schema') != 'factoryax.bundle.v1' or manifest.get('release') != 'HOLD'
            or manifest.get('signature') != 'UNSIGNED' or
            set(p.name for p in dest.iterdir()) != set(files) | {'QA_MANIFEST.json'}):
        raise ValueError('PACKAGE_SCHEMA_OR_FILES_INVALID')
    for name, expected in files.items():
        p = dest / name
        if p.is_symlink() or not p.is_file() or sha(p.read_bytes()) != expected:
            raise ValueError('PACKAGE_FILE_DRIFT')
    path = dest / 'FactoryAX-VERIFY.pyz'
    with zipfile.ZipFile(path) as arc:
        names = arc.namelist()
        if len(names) != len(set(names)) or set(names) != set(FILES) | {'__main__.py'}:
            raise ValueError('PACKAGE_ZIP_ENTRIES_INVALID')
        if any('/' not in name and name != '__main__.py' for name in names):
            raise ValueError('PACKAGE_MEMBER_INVALID')
        for name, expected in manifest['zip_member_sha256'].items():
            if sha(arc.read(name)) != expected:
                raise ValueError('PACKAGE_ZIP_SOURCE_DRIFT')
        if arc.read('__main__.py') != MAIN.encode():
            raise ValueError('PACKAGE_ENTRYPOINT_DRIFT')
    return {'status': 'INTEGRITY_OK', 'release': 'HOLD', 'signature': 'UNSIGNED',
            'file_count': len(files)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args(argv)
    try:
        dest = Path(args.output).absolute()
        result = validate(dest) if args.verify else build(Path(__file__).resolve().parents[1], dest)
        print(json.dumps({'status': 'OK', 'result': result}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)}, ensure_ascii=False))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
