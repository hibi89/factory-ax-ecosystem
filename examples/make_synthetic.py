"""Generate only invented factory exports and their explicit approval manifest."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROLES = ('purchase_order', 'production', 'quality_inspection', 'shipment')
HEAD = ['record_id', 'order_id', 'item_id', 'lot_id', 'quantity', 'unit']


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        raise SystemExit('usage: python examples/make_synthetic.py /absolute/new/demo')
    root = Path(argv[0]).absolute()
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'input'
    inputs.mkdir()
    spec = {'schema_version': 'factoryax.v0', 'human_approved': True,
            'profile_version': 'demo-1.0.0', 'rule_set_version': 'quality-v0.1',
            'approved_root': str(inputs), 'approved_units': ['EA'], 'files': {}}
    for role in ROLES:
        cols = HEAD + (['inspection_status'] if role == 'quality_inspection' else [])
        row = [role + '-01', 'PO-SYN-001', 'PART-SYN-01', 'LOT-SYN-7', '12.50', 'EA']
        if role == 'quality_inspection':
            row += ['PASS']
        file = inputs / f'{role}.csv'
        with file.open('w', newline='', encoding='utf-8-sig') as output:
            writer = csv.writer(output)
            writer.writerow(cols)
            writer.writerow(row)
        spec['files'][role] = {'path': file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                               'mapping': {name: name for name in cols}}
    (root / 'approved.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Synthetic demo (no customer data):', root)


if __name__ == '__main__':
    main()
