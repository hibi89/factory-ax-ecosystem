"""Hostile local JSON shapes must fail closed (no traceback or output)."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from factoryax.delivery import run
from factoryax.backup import backup

BASE = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


class MalformedExternalShapeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        subprocess.run([sys.executable, str(BASE / 'examples/make_reconcile_synthetic.py'),
                        str(self.root / 'approved')], check=True, capture_output=True)
        self.spec = self.root / 'approved' / 'approved.json'
        self.report = self.root / 'report'

    def blocked(self, *args):
        process = subprocess.run([sys.executable, '-m', 'factoryax', *map(str, args)],
                                 cwd=BASE, capture_output=True, text=True)
        self.assertEqual(process.returncode, 3, process.stdout + process.stderr)
        self.assertNotIn('Traceback', process.stderr)
        self.assertEqual(json.loads(process.stdout)['status'], 'BLOCKED')

    def reseal_report(self, report_json=None, receipt_json=None):
        if report_json is not None:
            raw = (json.dumps(report_json) + '\n').encode()
            (self.report / 'result.json').write_bytes(raw)
        receipt = json.loads((self.report / 'receipt.json').read_bytes())
        if receipt_json is not None:
            receipt.update(receipt_json)
        if report_json is not None:
            receipt['sha256']['result.json'] = sha((self.report / 'result.json').read_bytes())
        receipt_raw = (json.dumps(receipt, sort_keys=True) + '\n').encode()
        (self.report / 'receipt.json').write_bytes(receipt_raw)
        (self.report / 'COMPLETE.sha256').write_text(sha(receipt_raw) + '\n')

    def test_non_object_spec_fails_closed(self):
        self.spec.write_text('[]', encoding='utf-8')
        target = self.root / 'no-output'
        self.blocked('--spec', self.spec, '--output', target)
        self.assertFalse(target.exists())

    def test_receipt_wrong_sha_shape_fails_closed(self):
        run(self.spec, self.report)
        self.reseal_report(receipt_json={'sha256': 7})
        self.blocked('--verify-report', self.report)

    def test_result_wrong_json_shape_fails_closed(self):
        run(self.spec, self.report)
        self.reseal_report(report_json=[])
        self.blocked('--verify-report', self.report)

    def test_backup_metadata_wrong_json_shape_fails_closed(self):
        run(self.spec, self.report)
        original = self.root / 'original.zip'
        backup(self.report, original)
        with ZipFile(original, 'r') as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        parts['BACKUP_MANIFEST.json'] = b'[]'
        malicious = self.root / 'malformed.zip'
        with ZipFile(malicious, 'w', ZIP_DEFLATED) as archive:
            for name, content in parts.items():
                archive.writestr(name, content)
        restored = self.root / 'never-restored'
        self.blocked('--restore-backup', malicious, '--output', restored)
        self.assertFalse(restored.exists())


if __name__ == '__main__':
    unittest.main()
