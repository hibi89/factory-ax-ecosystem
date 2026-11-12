"""Create only invented four-role synthetic sample with one-to-many manufacturing.

No real data, accounts, secrets, network or customer document dependencies.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

BASE = ['record_id', 'order_id', 'item_id', 'lot_id', 'quantity', 'unit', 'event_date']
CASES = {
    'purchase_order': [['PO1', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '10', 'EA', '2026-11-01']],
    'production': [['P1', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '3', 'EA', '2026-11-02', 'NEW'],
                   ['P2', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '7', 'EA', '2026-11-03', 'NEW']],
    'quality_inspection': [['Q1', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '3', 'EA', '2026-11-04', 'PASS'],
                           ['Q2', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '7', 'EA', '2026-11-05', 'PASS']],
    'shipment': [['S1', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '5', 'EA', '2026-11-06', 'SHIP'],
                 ['S2', 'O-DEMO-1', 'PART-DEMO-1', 'LOT-DEMO-1', '5', 'EA', '2026-11-07', 'SHIP']],
}


def main(args=None):
    args = sys.argv[1:] if args is None else args
    if len(args) != 1:
        raise SystemExit('usage: python examples/make_reconcile_synthetic.py /absolute/new/directory')
    root = Path(args[0]).absolute()
    root.mkdir(parents=True, exist_ok=False)
    (root / 'input').mkdir()
    policy = {
        'policy_id': 'DEMO-01', 'policy_version': '1.0.0', 'approved_by': 'synthetic-owner',
        'period_start': '2026-11-01', 'period_end': '2026-11-30',
        'allow_partial_production': False, 'allow_partial_inspection': False,
        'allow_partial_shipment': False, 'allow_returns': False, 'allow_rework': False,
        'quantity_tolerance': '0'
    }
    spec = {'schema_version': 'factoryax.v0', 'human_approved': True, 'profile_version': 'demo-70',
            'rule_set_version': 'synthetic-reconcile-1', 'approved_root': str(root / 'input'),
            'approved_units': ['EA'], 'reconciliation_policy': policy, 'files': {}}
    for role, rows in CASES.items():
        header = BASE + (['inspection_status'] if role == 'quality_inspection'
                         else ['movement_kind'] if role in ('production', 'shipment') else [])
        path = root / 'input' / f'{role}.csv'
        with path.open('w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        spec['files'][role] = {'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                               'mapping': {key: key for key in header}}
    (root / 'approved.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Created invented four-stage demo at:', root)


if __name__ == '__main__':
    main()
