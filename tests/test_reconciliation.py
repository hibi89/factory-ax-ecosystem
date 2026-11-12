"""Independent synthetic business-case oracle (not generated from reconcile implementation)."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from factoryax.verify import verify, main, IntakeError

ROLES = ('purchase_order', 'production', 'quality_inspection', 'shipment')
BASE = ['record_id', 'order_id', 'item_id', 'lot_id', 'quantity', 'unit', 'event_date']
ROWS = {
    'purchase_order': [['PO1', 'O-1', 'P-1', 'L-1', '10', 'EA', '2026-11-01']],
    'production': [['P1', 'O-1', 'P-1', 'L-1', '3', 'EA', '2026-11-02', 'NEW'],
                   ['P2', 'O-1', 'P-1', 'L-1', '7', 'EA', '2026-11-03', 'NEW']],
    'quality_inspection': [['Q1', 'O-1', 'P-1', 'L-1', '3', 'EA', '2026-11-04', 'PASS'],
                           ['Q2', 'O-1', 'P-1', 'L-1', '7', 'EA', '2026-11-05', 'PASS']],
    'shipment': [['S1', 'O-1', 'P-1', 'L-1', '5', 'EA', '2026-11-06', 'SHIP'],
                 ['S2', 'O-1', 'P-1', 'L-1', '5', 'EA', '2026-11-07', 'SHIP']],
}


def headers(role):
    return BASE + (['inspection_status'] if role == 'quality_inspection'
                   else ['movement_kind'] if role in ('production', 'shipment') else [])


class ReconciliationTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.input = self.root / 'input'
        self.input.mkdir()
        self.rows = {role: [r[:] for r in values] for role, values in ROWS.items()}
        self.spec = {
            'schema_version': 'factoryax.v0', 'human_approved': True,
            'profile_version': 'synthetic-2026-11', 'rule_set_version': 'business-rules-1',
            'approved_root': str(self.input), 'approved_units': ['EA', 'KG'],
            'reconciliation_policy': {
                'policy_id': 'DEMO-01', 'policy_version': '1.0.0', 'approved_by': 'synthetic-owner',
                'period_start': '2026-11-01', 'period_end': '2026-11-30',
                'allow_partial_production': False, 'allow_partial_inspection': False,
                'allow_partial_shipment': False, 'allow_returns': False, 'allow_rework': False,
                'quantity_tolerance': '0',
            },
            'files': {},
        }

    def refresh(self):
        for role, rows in self.rows.items():
            buf = io.StringIO(newline='')
            writer = csv.writer(buf)
            writer.writerow(headers(role))
            writer.writerows(rows)
            content = buf.getvalue().encode('utf-8-sig')
            filename = role + '.csv'
            (self.input / filename).write_bytes(content)
            self.spec['files'][role] = {
                'path': filename, 'sha256': hashlib.sha256(content).hexdigest(),
                'mapping': {name: name for name in headers(role)},
            }

    def check(self, expected_status='OK', expected=()):
        self.refresh()
        result = verify(self.spec)
        codes = {x['code'] for x in result['findings']}
        self.assertEqual(result['status'], expected_status, codes)
        self.assertTrue(set(expected).issubset(codes), (expected, codes))
        self.assertEqual(result['scope'], 'W1-70: conservative four-stage reconciliation')
        self.assertEqual(result['reconciliation']['policy_version'], '1.0.0')
        for f in result['findings']:
            self.assertNotIn('O-1', json.dumps(f))
            self.assertTrue(all(x['row'] >= 2 for x in f['source_refs']))
        return result

    def test_D01_four_stage_exact(self):
        self.assertEqual(self.check()['reconciliation']['groups_checked'], 1)

    def test_D02_one_to_many_split_shipment(self):
        self.assertEqual(len(self.rows['production']), 2)
        self.assertEqual(len(self.rows['shipment']), 2)
        self.check()

    def test_D02_partial_shipment_explicitly_allowed(self):
        self.rows['shipment'][1][4] = '2'
        self.spec['reconciliation_policy']['allow_partial_shipment'] = True
        self.check()

    def test_D02_partial_shipment_denied(self):
        self.rows['shipment'][1][4] = '2'
        self.check('REVIEW_REQUIRED', ['SHIPMENT_INCOMPLETE'])

    def test_D03_wrong_lot_holds(self):
        self.rows['shipment'][0][3] = 'L-OTHER'
        self.check('REVIEW_REQUIRED', ['ORPHAN_ORDER_ITEM_LOT', 'INCOMPLETE_FOUR_STAGE_JOIN'])

    def test_D03_wrong_item_holds(self):
        self.rows['production'][0][2] = 'P-OTHER'
        self.check('REVIEW_REQUIRED', ['ORPHAN_ORDER_ITEM_LOT'])

    def test_D03_duplicate_row_identifier_holds(self):
        self.rows['production'][1][0] = 'P1'
        self.check('REVIEW_REQUIRED', ['DUPLICATE_RECORD_ID'])

    def test_D04_inspection_fail_never_shippable(self):
        self.rows['quality_inspection'][1][-1] = 'FAIL'
        self.check('REVIEW_REQUIRED', ['INSPECTION_NOT_PASS', 'SHIPMENT_EXCEEDS_PASSED_INSPECTION'])

    def test_D04_return_explicit_approval(self):
        self.rows['shipment'].append(['RET1', 'O-1', 'P-1', 'L-1', '2', 'EA', '2026-11-08', 'RETURN'])
        self.spec['reconciliation_policy'].update(allow_returns=True, allow_partial_shipment=True)
        self.check()

    def test_D04_return_exceeds_shipments(self):
        self.rows['shipment'].append(['RET1', 'O-1', 'P-1', 'L-1', '11', 'EA', '2026-11-08', 'RETURN'])
        self.spec['reconciliation_policy'].update(allow_returns=True, allow_partial_shipment=True)
        self.check('REVIEW_REQUIRED', ['RETURNS_EXCEED_SHIPMENTS'])

    def test_D04_unapproved_return_holds(self):
        self.rows['shipment'].append(['RET1', 'O-1', 'P-1', 'L-1', '2', 'EA', '2026-11-08', 'RETURN'])
        self.check('REVIEW_REQUIRED', ['MOVEMENT_NOT_APPROVED'])

    def test_D04_rework_not_double_counted(self):
        self.rows['production'].append(['R1', 'O-1', 'P-1', 'L-1', '3', 'EA', '2026-11-04', 'REWORK'])
        self.spec['reconciliation_policy']['allow_rework'] = True
        self.check()

    def test_D04_rework_exceeds_original(self):
        self.rows['production'].append(['R1', 'O-1', 'P-1', 'L-1', '11', 'EA', '2026-11-04', 'REWORK'])
        self.spec['reconciliation_policy']['allow_rework'] = True
        self.check('REVIEW_REQUIRED', ['REWORK_EXCEEDS_PRODUCTION'])

    def test_D05_precise_decimal_no_float(self):
        for role in ROLES:
            for row in self.rows[role]:
                row[4] = str(__import__('decimal').Decimal(row[4]) * __import__('decimal').Decimal('.0000000001'))
        self.check()

    def test_D05_units_not_cross_convert(self):
        self.rows['shipment'][1][5] = 'KG'
        self.check('REVIEW_REQUIRED', ['JOIN_UNIT_MISMATCH'])

    def test_D05_date_outside_period(self):
        self.rows['shipment'][0][6] = '2026-12-01'
        self.check('REVIEW_REQUIRED', ['EVENT_OUTSIDE_POLICY_PERIOD'])

    def test_D05_invalid_date(self):
        self.rows['shipment'][0][6] = '2026-11-31'
        self.check('REVIEW_REQUIRED', ['INVALID_EVENT_DATE'])

    def test_D05_later_pass_cannot_justify_early_shipment(self):
        self.rows['shipment'][0][6] = '2026-11-04'
        self.check('REVIEW_REQUIRED', ['TEMPORAL_SHIPMENT_UNSUPPORTED'])

    def test_D05_same_day_causal_order_without_time_holds(self):
        self.rows['quality_inspection'][0][6] = '2026-11-02'
        self.check('REVIEW_REQUIRED', ['TEMPORAL_INSPECTION_UNSUPPORTED'])

    def test_D05_return_before_original_ship_holds(self):
        self.rows['shipment'].append(['RET1', 'O-1', 'P-1', 'L-1', '2', 'EA', '2026-11-03', 'RETURN'])
        self.spec['reconciliation_policy'].update(allow_returns=True, allow_partial_shipment=True)
        self.check('REVIEW_REQUIRED', ['TEMPORAL_RETURN_UNSUPPORTED'])

    def test_D05_shipment_before_inspection(self):
        self.rows['shipment'][0][6] = '2026-11-03'
        self.check('REVIEW_REQUIRED', ['SHIPMENT_BEFORE_PASSED_INSPECTION'])

    def test_D05_overproduction(self):
        self.rows['production'][1][4] = '9'
        self.check('REVIEW_REQUIRED', ['PRODUCTION_EXCEEDS_ORDER'])

    def test_D06_invalid_policy_blocks_without_output(self):
        self.spec['reconciliation_policy']['quantity_tolerance'] = '1000'
        self.refresh()
        with self.assertRaisesRegex(IntakeError, 'RECONCILIATION_PERIOD_OR_TOLERANCE_INVALID'):
            verify(self.spec)
        config = self.root / 'approved.json'
        config.write_text(json.dumps(self.spec), encoding='utf-8')
        out = self.root / 'should-not-exist'
        self.assertEqual(main(['--spec', str(config), '--output', str(out)]), 3)
        self.assertFalse(out.exists())

    def test_D06_missing_movement_mapping_blocks(self):
        self.refresh()
        self.spec['files']['shipment']['mapping'].pop('movement_kind')
        with self.assertRaisesRegex(IntakeError, 'RECONCILIATION_MAPPING_REQUIRED'):
            verify(self.spec)

    def test_D07_readonly_and_D08_new_only_idempotence(self):
        self.refresh()
        original = {x.name: hashlib.sha256(x.read_bytes()).hexdigest() for x in self.input.iterdir()}
        config = self.root / 'approved.json'
        config.write_text(json.dumps(self.spec), encoding='utf-8')
        out = self.root / 'first'
        self.assertEqual(main(['--spec', str(config), '--output', str(out)]), 0)
        self.assertEqual(main(['--spec', str(config), '--output', str(out)]), 3)
        self.assertEqual(original, {x.name: hashlib.sha256(x.read_bytes()).hexdigest() for x in self.input.iterdir()})
        self.assertEqual(json.loads((out / 'result.json').read_text())['reconciliation']['groups_checked'], 1)

    def test_D08_sha_drift_blocks(self):
        self.refresh()
        (self.input / 'production.csv').write_bytes(b'forged')
        with self.assertRaisesRegex(IntakeError, 'SOURCE_SHA_DRIFT'):
            verify(self.spec)

    def test_quality_partial_inspection_denied(self):
        self.rows['quality_inspection'][1][4] = '2'
        self.spec['reconciliation_policy']['allow_partial_shipment'] = True
        self.check('REVIEW_REQUIRED', ['INSPECTION_INCOMPLETE', 'SHIPMENT_EXCEEDS_PASSED_INSPECTION'])

    def test_unknown_movement_holds(self):
        self.rows['shipment'][1][-1] = 'EXCHANGE'
        self.check('REVIEW_REQUIRED', ['UNKNOWN_MOVEMENT_KIND'])

    def test_empty_join_blocks_auto_ok(self):
        self.rows['shipment'][0][4] = 'bad'
        self.rows['shipment'][1][4] = 'bad'
        self.check('REVIEW_REQUIRED', ['INVALID_QUANTITY', 'INCOMPLETE_FOUR_STAGE_JOIN'])


if __name__ == '__main__':
    unittest.main()
