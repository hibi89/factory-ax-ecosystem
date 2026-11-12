import csv
import io
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from factoryax.verify import verify, export_new, IntakeError, main

ROLES = ('purchase_order', 'production', 'quality_inspection', 'shipment')
HEAD = ('record_id', 'order_id', 'item_id', 'lot_id', 'quantity', 'unit')


def make_xlsx(headers, records, bad_formula=False, hidden=False, extra=None):
    def col(i):
        s = ''
        while i:
            i, r = divmod(i - 1, 26)
            s = chr(65+r) + s
        return s
    xml_rows = []
    for n, row in enumerate([headers] + records, 1):
        cells = []
        for index, value in enumerate(row, 1):
            if bad_formula and n == 2 and index == 5:
                cells.append(f'<c r="{col(index)}{n}"><f>1+1</f><v>2</v></c>')
            else:
                cells.append(f'<c r="{col(index)}{n}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
        xml_rows.append(f'<row r="{n}">' + ''.join(cells) + '</row>')
    sheet = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' + ''.join(xml_rows) + '</sheetData></worksheet>'
    book = '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Sheet1" sheetId="1"' + (' state="hidden"' if hidden else '') + '/></sheets></workbook>'
    stream = io.BytesIO()
    with ZipFile(stream, 'w', ZIP_DEFLATED) as z:
        z.writestr('xl/workbook.xml', book)
        z.writestr('xl/worksheets/sheet1.xml', sheet)
        if extra:
            z.writestr(extra, 'malicious')
    return stream.getvalue()


def make_csv(headers, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8-sig')


class VerifyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / '승인된 입력'
        self.root.mkdir()
        self.spec = {'schema_version': 'factoryax.v0', 'human_approved': True, 'profile_version': '1.0.0',
                     'rule_set_version': 'rule-v1', 'approved_root': str(self.root),
                     'approved_units': ['EA'], 'files': {}}
        for role in ROLES:
            headers = HEAD + (('inspection_status',) if role == 'quality_inspection' else ())
            row = [role + '-1', 'O-001', 'ITEM-A', 'LOT-7', '1.25', 'EA'] + (['PASS'] if role == 'quality_inspection' else [])
            self.install(role, headers, [row])

    def install(self, role, headers, records, extension='.csv', **kw):
        filename = role + extension
        data = make_xlsx(headers, records, **kw) if extension == '.xlsx' else make_csv(headers, records)
        path = self.root / filename
        path.write_bytes(data)
        self.spec['files'][role] = {'path': filename, 'sha256': hashlib.sha256(data).hexdigest(),
                                   'mapping': {h: h for h in headers}}
        return path

    def codes(self):
        return {x['code'] for x in verify(self.spec)['findings']}

    def test_four_csv_ok(self):
        self.assertEqual(verify(self.spec)['status'], 'OK')
        self.assertEqual(sum(verify(self.spec)['record_counts'].values()), 4)

    def test_four_xlsx_ok(self):
        for role in ROLES:
            self.install(role, tuple(self.spec['files'][role]['mapping']),
                         [[role+'-1', 'O-001', 'ITEM-A', 'LOT-7', '1.25', 'EA'] + (['PASS'] if role == 'quality_inspection' else [])], '.xlsx')
        self.assertEqual(verify(self.spec)['status'], 'OK')

    def test_mixed_xlsx_csv(self):
        self.install('shipment', HEAD, [['ship-2', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA']], '.xlsx')
        self.assertEqual(verify(self.spec)['status'], 'OK')

    def test_sha_drift(self):
        (self.root / 'shipment.csv').write_bytes(b'forged')
        with self.assertRaisesRegex(IntakeError, 'SOURCE_SHA_DRIFT'):
            verify(self.spec)

    def test_unapproved_spec(self):
        self.spec['human_approved'] = False
        with self.assertRaisesRegex(IntakeError, 'APPROVED_SPEC_REQUIRED'):
            verify(self.spec)

    def test_missing_role(self):
        del self.spec['files']['shipment']
        with self.assertRaisesRegex(IntakeError, 'FOUR_ROLES_REQUIRED'):
            verify(self.spec)

    def test_traversal_denied(self):
        self.spec['files']['shipment']['path'] = '../shipment.csv'
        with self.assertRaisesRegex(IntakeError, 'PATH_OUTSIDE_APPROVED_ROOT'):
            verify(self.spec)

    def test_absolute_denied(self):
        self.spec['files']['shipment']['path'] = str(self.root / 'shipment.csv')
        # Native Windows absolute paths contain backslashes and are rejected
        # as PATH_INVALID before absolute-path detection. Both are fail-closed.
        denial = 'PATH_INVALID' if os.name == 'nt' else 'PATH_OUTSIDE_APPROVED_ROOT'
        with self.assertRaisesRegex(IntakeError, denial):
            verify(self.spec)

    def test_symlink_denied(self):
        outside = self.base / 'outside.csv'
        outside.write_bytes((self.root / 'shipment.csv').read_bytes())
        (self.root / 'shipment.csv').unlink()
        (self.root / 'shipment.csv').symlink_to(outside)
        with self.assertRaisesRegex(IntakeError, 'SYMLINK_DENIED'):
            verify(self.spec)

    def test_missing_required(self):
        self.install('shipment', HEAD, [['s', 'O-001', '', 'LOT-7', '1.25', 'EA']])
        self.assertIn('MISSING_REQUIRED_ITEM_ID', self.codes())

    def test_duplicate_record_id(self):
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '1.25', 'EA'],
                                        ['s', 'O-001', 'ITEM-A', 'LOT-7', '1.25', 'EA']])
        self.assertIn('DUPLICATE_RECORD_ID', self.codes())

    def test_orphan_key(self):
        self.install('shipment', HEAD, [['s', 'O-002', 'ITEM-A', 'LOT-7', '1.25', 'EA']])
        self.assertIn('ORPHAN_ORDER_ITEM_LOT', self.codes())

    def test_invalid_quantities(self):
        self.install('shipment', HEAD, [[f's{i}', 'O-001', 'ITEM-A', 'LOT-7', q, 'EA'] for i, q in enumerate(['NaN', '-1', '0', 'xyz'])])
        self.assertEqual([f['code'] for f in verify(self.spec)['findings']].count('INVALID_QUANTITY'), 4)

    def test_decimal_precise(self):
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '0.00000000000000000001', 'EA']])
        self.assertEqual(verify(self.spec)['status'], 'OK')

    def test_unapproved_unit(self):
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '1', 'BOX']])
        self.assertIn('UNAPPROVED_UNIT', self.codes())

    def test_bad_inspection(self):
        self.install('quality_inspection', HEAD + ('inspection_status',), [['q', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA', 'PASS!']])
        self.assertIn('UNKNOWN_INSPECTION_STATUS', self.codes())

    def test_duplicate_header_blocked(self):
        self.install('shipment', HEAD + ('unit',), [['s', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA', 'EA']])
        with self.assertRaisesRegex(IntakeError, 'HEADERS_INVALID'):
            verify(self.spec)

    def test_header_mapping_not_approved(self):
        self.spec['files']['shipment']['mapping']['quantity'] = 'unmapped'
        with self.assertRaisesRegex(IntakeError, 'MAPPING_UNAPPROVED_OR_MISSING'):
            verify(self.spec)

    def test_xlsx_formula_blocked(self):
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA']], '.xlsx', bad_formula=True)
        with self.assertRaisesRegex(IntakeError, 'XLSX_FORMULA_DENIED'):
            verify(self.spec)

    def test_xlsx_hidden_sheet_blocked(self):
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA']], '.xlsx', hidden=True)
        with self.assertRaisesRegex(IntakeError, 'XLSX_SINGLE_VISIBLE_SHEET_ONLY'):
            verify(self.spec)

    def test_xlsx_vba_blocked(self):
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA']], '.xlsx', extra='xl/vbaProject.bin')
        with self.assertRaisesRegex(IntakeError, 'XLSX_UNSAFE_CONTENT'):
            verify(self.spec)

    def test_xlsx_bogus_magic(self):
        path = self.root / 'shipment.xlsx'
        path.write_bytes(b'not a zip')
        self.spec['files']['shipment']['path'] = path.name
        self.spec['files']['shipment']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(IntakeError, 'XLSX_MAGIC_INVALID'):
            verify(self.spec)

    def test_invalid_unicode(self):
        path = self.root / 'shipment.csv'
        path.write_bytes(b'\xff\xff')
        self.spec['files']['shipment']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(IntakeError, 'CSV_UTF8_REQUIRED'):
            verify(self.spec)

    def test_export_and_no_overwrite(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir()}
        output = self.base / 'result-new'
        export_new(verify(self.spec), output)
        self.assertEqual(set(p.name for p in output.iterdir()), {'result.json', 'summary.csv', 'summary.html'})
        self.assertEqual(json.loads((output / 'result.json').read_text(encoding='utf-8'))['status'], 'OK')
        self.assertNotIn('ITEM-A', (output / 'summary.html').read_text(encoding='utf-8'))
        with self.assertRaisesRegex(IntakeError, 'OUTPUT_EXISTS_NO_OVERWRITE'):
            export_new(verify(self.spec), output)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir()})

    def test_cli_ok_and_review(self):
        specfile = self.base / 'approved.json'
        specfile.write_text(json.dumps(self.spec))
        self.assertEqual(main(['--spec', str(specfile), '--output', str(self.base / 'ok')]), 0)
        self.install('shipment', HEAD, [['s', 'O-001', 'ITEM-A', 'LOT-7', '0', 'EA']])
        specfile.write_text(json.dumps(self.spec))
        self.assertEqual(main(['--spec', str(specfile), '--output', str(self.base / 'review')]), 2)

    def test_cli_blocked_no_outputs(self):
        specfile = self.base / 'approved.json'
        self.spec['files']['shipment']['sha256'] = '0' * 64
        specfile.write_text(json.dumps(self.spec))
        output = self.base / 'should-not-exist'
        self.assertEqual(main(['--spec', str(specfile), '--output', str(output)]), 3)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()

# Additional regression cases; no customer data or external API use.
class AuditBoundaryTest(VerifyTest):
    def test_bad_quality_result_review(self):
        self.install('quality_inspection', HEAD + ('inspection_status',),
                     [['q', 'O-001', 'ITEM-A', 'LOT-7', '1', 'EA', 'FAIL']])
        self.assertIn('INSPECTION_NOT_PASS', self.codes())

    def test_csv_formula_payload_is_not_executed_or_exported(self):
        self.install('shipment', HEAD, [['s', 'O-001', '=cmd|', 'LOT-7', '1', 'EA']])
        r = verify(self.spec)
        self.assertEqual(r['status'], 'REVIEW_REQUIRED')
        output = self.base / 'review'
        export_new(r, output)
        self.assertNotIn('=cmd', (output / 'summary.csv').read_text(encoding='utf-8-sig'))
        self.assertNotIn('=cmd', (output / 'result.json').read_text(encoding='utf-8'))

