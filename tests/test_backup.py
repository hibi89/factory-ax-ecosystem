"""Synthetic report backup/restore negative and positive checks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
from unittest.mock import patch

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

    def test_backup_output_via_symlinked_ancestor_denied(self):
        alias = self.root / 'backup-alias'
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('directory symlink unsupported by this OS')
        with self.assertRaisesRegex(IntakeError, 'UNSAFE_DIRECTORY_ANCESTOR'):
            backup(self.report, alias / 'safe.zip')
        self.assertFalse(self.zip.exists())

    def test_restore_output_via_symlinked_ancestor_denied(self):
        backup(self.report, self.zip)
        alias = self.root / 'restore-alias'
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('directory symlink unsupported by this OS')
        with self.assertRaisesRegex(IntakeError, 'UNSAFE_DIRECTORY_ANCESTOR'):
            restore(self.zip, alias / 'new-restored')
        self.assertFalse((self.root / 'new-restored').exists())

    def test_restore_zip_via_symlinked_ancestor_denied(self):
        backup(self.report, self.zip)
        alias = self.root / 'zip-alias'
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('directory symlink unsupported by this OS')
        with self.assertRaisesRegex(IntakeError, 'UNSAFE_DIRECTORY_ANCESTOR'):
            restore(alias / 'safe.zip', self.restored)
        self.assertFalse(self.restored.exists())

    def test_repeated_backup_cannot_overwrite(self):
        backup(self.report, self.zip)
        before = self.zip.read_bytes()
        with self.assertRaisesRegex(IntakeError, 'BACKUP_TARGET'):
            backup(self.report, self.zip)
        self.assertEqual(before, self.zip.read_bytes())

    def test_backup_rejects_source_mutation_after_initial_verification(self):
        authentic_verify = verify_candidate
        mutated = False

        def change_after_verification(directory):
            nonlocal mutated
            result = authentic_verify(directory)
            if not mutated:
                mutated = True
                (self.report / 'summary.csv').write_bytes(b'changed after verified')
            return result

        with patch('factoryax.backup.verify_candidate', side_effect=change_after_verification):
            with self.assertRaisesRegex(IntakeError, 'BACKUP_SOURCE_CHANGED_DURING_CAPTURE'):
                backup(self.report, self.zip)
        self.assertFalse(self.zip.exists())

    def test_backup_rejects_source_mutation_during_archive_write(self):
        genuine_write = ZipFile.writestr
        mutated = False

        def mutate_on_first_archive_member(archive, *args, **kwargs):
            nonlocal mutated
            if not mutated:
                mutated = True
                (self.report / 'summary.csv').write_bytes(b'changed while writing')
            return genuine_write(archive, *args, **kwargs)

        with patch.object(ZipFile, 'writestr', mutate_on_first_archive_member):
            with self.assertRaisesRegex(IntakeError, 'REPORT_FILE_DRIFT'):
                backup(self.report, self.zip)
        self.assertFalse(self.zip.exists())

    def test_backup_competing_writer_race_never_deletes_winner(self):
        # Reproduce TOCTOU between initial not-exists check and 'xb' open.
        original_open = Path.open
        winner = b'COMPETING PROCESS PRIVATE FILE - MUST NOT DELETE'

        def competitor_open(path, mode='r', *args, **kwargs):
            if path == self.zip and mode == 'xb':
                self.zip.write_bytes(winner)
                raise FileExistsError('competitor won exclusive creation')
            return original_open(path, mode, *args, **kwargs)

        with patch.object(Path, 'open', competitor_open):
            with self.assertRaises(FileExistsError):
                backup(self.report, self.zip)
        self.assertEqual(self.zip.read_bytes(), winner)

    def test_backup_write_failure_only_cleans_own_inode(self):
        import os
        original_fsync = os.fsync
        called = 0

        def fail_first_fsync(fd):
            nonlocal called
            called += 1
            if called == 1:
                raise OSError('synthetic failure')
            return original_fsync(fd)

        with patch('factoryax.backup.os.fsync', side_effect=fail_first_fsync):
            with self.assertRaises(OSError):
                backup(self.report, self.zip)
        self.assertFalse(self.zip.exists())

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
