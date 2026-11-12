"""Synthetic report backup/restore negative and positive checks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from factoryax.delivery import IntakeError, run, verify_candidate
from factoryax.backup import backup, restore

BASE = Path(__file__).resolve().parents[1]


class BackupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = tempfile.TemporaryDirectory()
        subprocess.run([sys.executable, str(BASE / 'examples/make_reconcile_synthetic.py'),
                        str(Path(cls.demo.name) / 'fixtures')], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.demo.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = Path(self.demo.name) / 'fixtures' / 'approved.json'
        self.report = self.root / 'report'
        run(self.src, self.report)
        self.zip = self.root / 'safe.zip'
        self.restored = self.root / 'restored'

    def test_roundtrip(self):
        before = (self.report / 'result.json').read_bytes()
        receipt = backup(self.report, self.zip)
        self.assertEqual(receipt['status'], 'BACKUP_CREATED')
        restored = restore(self.zip, self.restored)
        self.assertEqual(restored['status'], 'RESTORED_AND_VERIFIED')
        self.assertEqual(before, (self.restored / 'result.json').read_bytes())
        self.assertEqual(verify_candidate(self.restored)['status'], 'OK')

    def test_repeated_backup_cannot_overwrite(self):
        backup(self.report, self.zip)
        before = self.zip.read_bytes()
        with self.assertRaisesRegex(IntakeError, 'BACKUP_TARGET'):
            backup(self.report, self.zip)
        self.assertEqual(before, self.zip.read_bytes())

    def test_repeated_restore_cannot_overwrite(self):
        backup(self.report, self.zip)
        restore(self.zip, self.restored)
        with self.assertRaisesRegex(IntakeError, 'RESTORE_TARGET'):
            restore(self.zip, self.restored)

    def test_bad_report_cannot_backup(self):
        (self.report / 'summary.csv').write_bytes(b'bad')
        with self.assertRaises(IntakeError):
            backup(self.report, self.zip)
        self.assertFalse(self.zip.exists())

    def test_modified_backup_rejected(self):
        backup(self.report, self.zip)
        original = {item.filename: data for item in [] for data in []}
        with ZipFile(self.zip) as archive:
            original = {name: archive.read(name) for name in archive.namelist()}
        original['result.json'] += b'wrong'
        with ZipFile(self.zip, 'w', compression=ZIP_DEFLATED) as archive:
            for name, data in original.items():
                archive.writestr(name, data)
        with self.assertRaisesRegex(IntakeError, 'BACKUP_INTEGRITY'):
            restore(self.zip, self.restored)
        self.assertFalse(self.restored.exists())

    def test_zip_slip_rejected(self):
        backup(self.report, self.zip)
        with ZipFile(self.zip, 'a') as archive:
            archive.writestr('../bad.txt', 'bad')
        with self.assertRaisesRegex(IntakeError, 'BACKUP_UNSAFE_ENTRIES'):
            restore(self.zip, self.restored)
        self.assertFalse((self.root / 'bad.txt').exists())

    def test_restore_existing_dir(self):
        backup(self.report, self.zip)
        self.restored.mkdir()
        with self.assertRaisesRegex(IntakeError, 'RESTORE_TARGET'):
            restore(self.zip, self.restored)

    def test_cli_backup_restore(self):
        for args in [('--backup-report', str(self.report), '--output', str(self.zip)),
                     ('--restore-backup', str(self.zip), '--output', str(self.restored))]:
            p = subprocess.run([sys.executable, '-m', 'factoryax', *args],
                               cwd=BASE, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(verify_candidate(self.restored)['status'], 'OK')

if __name__ == '__main__':
    unittest.main()
