"""Owner candidate integrity/packager and no-overwrite tests, synthetic only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from factoryax.delivery import (COMPLETE, IntakeError, export_candidate,
                                run, verify_candidate, _source_recheck)
from factoryax.verify import verify

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'scripts'))
from build_candidate import build, validate


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        script = BASE / 'examples' / 'make_reconcile_synthetic.py'
        subprocess.run([sys.executable, str(script), str(self.root / 'inputs')], check=True, capture_output=True)
        self.spec_path = self.root / 'inputs' / 'approved.json'
        self.out = self.root / 'new-report'

    def test_run_and_receipt(self):
        result = run(self.spec_path, self.out)
        self.assertEqual(result['status'], 'OK')
        self.assertEqual(verify_candidate(self.out)['files'], 3)
        self.assertEqual(set(p.name for p in self.out.iterdir()),
                         {'receipt.json', 'COMPLETE.sha256', 'result.json', 'summary.csv', 'summary.html'})

    def test_no_overwrite(self):
        run(self.spec_path, self.out)
        before = (self.out / 'result.json').read_bytes()
        with self.assertRaisesRegex(IntakeError, 'OUTPUT_EXISTS'):
            run(self.spec_path, self.out)
        self.assertEqual((self.out / 'result.json').read_bytes(), before)

    def test_existing_empty_folder_not_overwritten(self):
        self.out.mkdir()
        with self.assertRaisesRegex(IntakeError, 'OUTPUT_EXISTS'):
            run(self.spec_path, self.out)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_symlink_output_refused(self):
        destination = self.root / 'real'
        destination.mkdir()
        try:
            self.out.symlink_to(destination)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unsupported')
        with self.assertRaises(IntakeError):
            run(self.spec_path, self.out)

    def test_receipt_tamper(self):
        run(self.spec_path, self.out)
        (self.out / 'result.json').write_text('bad', encoding='utf-8')
        with self.assertRaisesRegex(IntakeError, 'REPORT_FILE_DRIFT'):
            verify_candidate(self.out)

    def test_complete_tamper(self):
        run(self.spec_path, self.out)
        (self.out / COMPLETE).write_text('0'*64+'\n')
        with self.assertRaisesRegex(IntakeError, 'REPORT_RECEIPT_DRIFT'):
            verify_candidate(self.out)

    def test_incomplete_folder_denied(self):
        self.out.mkdir()
        (self.out / 'result.json').write_text('{}')
        with self.assertRaisesRegex(IntakeError, 'REPORT_UNEXPECTED'):
            verify_candidate(self.out)

    def test_receipt_extra_file_denied(self):
        run(self.spec_path, self.out)
        (self.out / 'unapproved.csv').write_text('not approved')
        with self.assertRaisesRegex(IntakeError, 'REPORT_UNEXPECTED'):
            verify_candidate(self.out)

    def test_source_sha_drift(self):
        spec = json.loads(self.spec_path.read_text())
        report = verify(spec)
        original = self.root / 'inputs' / 'input' / spec['files']['shipment']['path']
        original.write_bytes(original.read_bytes() + b'\n')
        with self.assertRaisesRegex(IntakeError, 'SOURCE_SHA_DRIFT'):
            _source_recheck(spec, report)

    def test_failed_recheck_does_not_create_output(self):
        spec = json.loads(self.spec_path.read_text())
        report = verify(spec)
        spec['files']['shipment']['sha256'] = '0'*64
        with self.assertRaises(IntakeError):
            export_candidate(report, self.out, spec=spec)
        self.assertFalse(self.out.exists())

    def test_tampered_approval(self):
        spec = json.loads(self.spec_path.read_text())
        spec['human_approved'] = False
        self.spec_path.write_text(json.dumps(spec))
        with self.assertRaisesRegex(IntakeError, 'APPROVED_SPEC_REQUIRED'):
            run(self.spec_path, self.out)
        self.assertFalse(self.out.exists())

    def test_cli(self):
        result = subprocess.run([sys.executable, '-m', 'factoryax', '--spec', str(self.spec_path),
                                 '--output', str(self.out)], cwd=BASE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        result = subprocess.run([sys.executable, '-m', 'factoryax', '--verify-report', str(self.out)],
                                cwd=BASE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_zipapp_build_integrity_run(self):
        pkg = self.root / 'package'
        build(BASE, pkg)
        self.assertEqual(validate(pkg)['status'], 'INTEGRITY_OK')
        self.assertIn('RELEASE HOLD', (pkg / 'README_QA.txt').read_text())
        result = subprocess.run([sys.executable, str(pkg / 'FactoryAX-VERIFY.pyz'),
                                 '--spec', str(self.spec_path), '--output', str(self.out)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(verify_candidate(self.out)['status'], 'OK')

    def test_windows_launcher_preserves_blocked_exit_code(self):
        """Windows CMD expands %errorlevel% before a parenthesized block.

        The generated launcher must use separate command lines after a GOTO,
        so a 3/BLOCKED exit is not accidentally converted to 0/OK.
        Native behavior is checked by the Windows CI job, not this static test.
        """
        pkg = self.root / 'pkg'; build(BASE, pkg)
        batch = (pkg / 'RUN_VERIFY_WINDOWS.cmd').read_bytes().decode('ascii')
        self.assertIn('if errorlevel 1 goto use_python\r\n', batch)
        self.assertIn('py -3 "%~dp0FactoryAX-VERIFY.pyz" %*\r\nexit /b %errorlevel%\r\n', batch)
        self.assertIn('python "%~dp0FactoryAX-VERIFY.pyz" %*\r\nexit /b %errorlevel%\r\n', batch)
        self.assertNotIn('if %errorlevel% equ 0 (', batch)
        self.assertNotIn('!errorlevel!', batch)

    def test_deterministic_build(self):
        p = self.root / 'p'; q = self.root / 'q'
        build(BASE, p); build(BASE, q)
        self.assertEqual((p / 'FactoryAX-VERIFY.pyz').read_bytes(),
                         (q / 'FactoryAX-VERIFY.pyz').read_bytes())
        self.assertEqual((p / 'QA_MANIFEST.json').read_bytes(),
                         (q / 'QA_MANIFEST.json').read_bytes())

    def test_package_tamper(self):
        pkg = self.root / 'pkg'
        build(BASE, pkg)
        (pkg / 'RUN_VERIFY_WINDOWS.cmd').write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError, 'PACKAGE_FILE_DRIFT'):
            validate(pkg)

    def test_source_symlink_not_packaged(self):
        mirror = self.root / 'mirror'
        mirror.mkdir()
        (mirror / 'factoryax').mkdir()
        (mirror / 'factoryax' / '__init__.py').symlink_to(BASE / 'factoryax' / '__init__.py')
        with self.assertRaisesRegex(ValueError, 'SOURCE_MISSING_OR_SYMLINK'):
            build(mirror, self.root / 'zip')

    def test_no_optional_network_modules_in_bundle(self):
        pkg = self.root / 'pkg'; build(BASE, pkg)
        import zipfile
        with zipfile.ZipFile(pkg / 'FactoryAX-VERIFY.pyz') as arc:
            self.assertNotIn('requests', '\n'.join(arc.namelist()))
            self.assertNotIn('socket', '\n'.join(arc.namelist()))
            self.assertEqual(len(arc.namelist()), 8)

    def test_gui_declares_local_owner_scope(self):
        code = (BASE / 'factoryax' / 'gui.py').read_text(encoding='utf-8')
        self.assertIn('tkinter', code)
        self.assertIn('RELEASE HOLD', code)
        self.assertIn('run(spec.get(), output.get())', code)

    def test_receipt_is_unsigned(self):
        run(self.spec_path, self.out)
        r = json.loads((self.out / 'receipt.json').read_text())
        self.assertEqual(r['authenticity'], 'UNSIGNED_LOCAL_INTEGRITY_ONLY')
        self.assertEqual(r['release'], 'HOLD')

    def test_spec_mutation_rejected(self):
        spec = json.loads(self.spec_path.read_text())
        spec['files']['shipment']['sha256'] = '0'*64
        self.spec_path.write_text(json.dumps(spec))
        with self.assertRaises(IntakeError):
            run(self.spec_path, self.out)
        self.assertFalse(self.out.exists())

if __name__ == '__main__':
    unittest.main()
