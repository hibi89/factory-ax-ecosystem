"""Deterministic four-stage reconciliation for approved factory export snapshots.

Independent W1 module: no PREP/EAI source imported. No ERP write or AI verdict.
All currencies/units outside approved one-to-one symbol matching are held.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
import re

ROLES = ('purchase_order', 'production', 'quality_inspection', 'shipment')
POLICY_KEYS = frozenset({
    'policy_id', 'policy_version', 'approved_by', 'period_start', 'period_end',
    'allow_partial_production', 'allow_partial_inspection', 'allow_partial_shipment',
    'allow_returns', 'allow_rework', 'quantity_tolerance',
})
GROUP_STATUS = {'PASS', 'FAIL', 'REVIEW'}
OPTIONAL = {r: ('event_date',) for r in ROLES}
OPTIONAL['production'] = ('event_date', 'movement_kind')
OPTIONAL['shipment'] = ('event_date', 'movement_kind')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
IDENTIFIER_PATTERN = re.compile(r'^[A-Za-z0-9._-]{1,64}$')


class ReconciliationError(ValueError):
    """Invalid explicit policy or required mapping: no authoritative report."""


def parse_date(value):
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        raise ValueError('DATE_FORMAT')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError('DATE_INVALID') from exc


def validate_policy(spec):
    policy = spec.get('reconciliation_policy')
    if not isinstance(policy, dict) or set(policy) != POLICY_KEYS:
        raise ReconciliationError('RECONCILIATION_POLICY_EXPLICIT_FIELDS_REQUIRED')
    for field in ('policy_id', 'policy_version', 'approved_by'):
        if not isinstance(policy[field], str) or not IDENTIFIER_PATTERN.fullmatch(policy[field]):
            raise ReconciliationError('RECONCILIATION_POLICY_ID_REQUIRED')
    for flag in ('allow_partial_production', 'allow_partial_inspection',
                 'allow_partial_shipment', 'allow_returns', 'allow_rework'):
        if type(policy[flag]) is not bool:
            raise ReconciliationError('RECONCILIATION_POLICY_BOOLEAN_REQUIRED')
    try:
        start, end = parse_date(policy['period_start']), parse_date(policy['period_end'])
        tolerance = Decimal(policy['quantity_tolerance'])
    except (ValueError, TypeError, InvalidOperation) as exc:
        raise ReconciliationError('RECONCILIATION_PERIOD_OR_TOLERANCE_INVALID') from exc
    if start > end or (end - start).days > 366 or not tolerance.is_finite() or tolerance < 0 or tolerance > Decimal('0.000001'):
        raise ReconciliationError('RECONCILIATION_PERIOD_OR_TOLERANCE_INVALID')
    for role in ROLES:
        mapping = spec['files'][role].get('mapping', {})
        if not isinstance(mapping, dict) or not set(OPTIONAL[role]).issubset(mapping):
            raise ReconciliationError('RECONCILIATION_MAPPING_REQUIRED')
    return policy, start, end, tolerance


def _quantity(row):
    try:
        value = Decimal(row['quantity'])
        return value if value.is_finite() and value > 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def reconcile(spec, records, units):
    """Return limited rule findings and source-minimal evidence summary.

    Independent reconciler checks total source rows, not just the final valid ones;
    all findings are REVIEW_REQUIRED and never silently exclude invalid records.
    """
    policy, start, end, tolerance = validate_policy(spec)
    findings = []
    groups = defaultdict(lambda: defaultdict(list))
    dated = defaultdict(lambda: defaultdict(list))
    invalid = 0

    def finding(code, refs):
        # A bounded source citation list; no customer field value or path in reports.
        refs = sorted(set(refs), key=lambda x: (ROLES.index(x[0]), x[1]))
        findings.append({'code': code, 'status': 'REVIEW_REQUIRED',
                         'source_refs': [{'source_id': r, 'row': n} for r, n in refs[:12]],
                         'extra_refs_not_shown': max(0, len(refs) - 12),
                         'rule_id': f"factory-join-{policy['policy_version']}"})

    for role in ROLES:
        for row in records[role]:
            ref = (role, row['_row'])
            key = (row['order_id'], row['item_id'], row['lot_id'])
            q = _quantity(row)
            if not all(key) or q is None or row['unit'] not in units:
                invalid += 1
                # Baseline quality engine already emits a row-specific finding.
                continue
            try:
                current = parse_date(row['event_date'])
            except (ValueError, KeyError, TypeError):
                finding('INVALID_EVENT_DATE', [ref])
                invalid += 1
                continue
            if not start <= current <= end:
                finding('EVENT_OUTSIDE_POLICY_PERIOD', [ref])
                invalid += 1
                continue
            if role in ('production', 'shipment'):
                movement = row.get('movement_kind', '')
                approved = ('NEW', 'REWORK') if role == 'production' else ('SHIP', 'RETURN')
                if movement not in approved:
                    finding('UNKNOWN_MOVEMENT_KIND', [ref])
                    invalid += 1
                    continue
                if (movement == 'REWORK' and not policy['allow_rework']) or (movement == 'RETURN' and not policy['allow_returns']):
                    finding('MOVEMENT_NOT_APPROVED', [ref])
                    invalid += 1
                    continue
            groups[key][role].append((row, q, ref))
            dated[key][role].append(current)

    flagged_groups = 0
    for key, stages in sorted(groups.items()):
        all_entries = [entry for role in ROLES for entry in stages[role]]
        refs = [entry[2] for entry in all_entries]
        before = len(findings)
        unitset = {r['unit'] for r, _, _ in all_entries}
        if len(unitset) != 1:
            finding('JOIN_UNIT_MISMATCH', refs)
            flagged_groups += 1
            continue
        if any(not stages[role] for role in ROLES):
            finding('INCOMPLETE_FOUR_STAGE_JOIN', refs)
            flagged_groups += 1
            continue

        amount = lambda role, movement=None, status=None: sum((q for r, q, _ in stages[role]
            if (movement is None or r.get('movement_kind') == movement)
            and (status is None or r.get('inspection_status') == status)), Decimal(0))
        order = amount('purchase_order')
        produced = amount('production', 'NEW')
        reworked = amount('production', 'REWORK')
        passed = amount('quality_inspection', status='PASS')
        inspected = amount('quality_inspection')
        shipped = amount('shipment', 'SHIP')
        returned = amount('shipment', 'RETURN')
        # FAIL/REVIEW are never accepted as shippable quantities.
        if inspected - produced > tolerance:
            finding('INSPECTED_EXCEEDS_NEW_PRODUCTION', refs)
        if produced - order > tolerance:
            finding('PRODUCTION_EXCEEDS_ORDER', refs)
        if shipped - passed > tolerance:
            finding('SHIPMENT_EXCEEDS_PASSED_INSPECTION', refs)
        if shipped - order > tolerance:
            finding('SHIPMENT_EXCEEDS_ORDER', refs)
        if returned - shipped > tolerance:
            finding('RETURNS_EXCEED_SHIPMENTS', refs)
        if reworked - produced > tolerance:
            finding('REWORK_EXCEEDS_PRODUCTION', refs)
        if not policy['allow_partial_production'] and order - produced > tolerance:
            finding('PRODUCTION_INCOMPLETE', refs)
        if not policy['allow_partial_inspection'] and produced - inspected > tolerance:
            finding('INSPECTION_INCOMPLETE', refs)
        if not policy['allow_partial_shipment'] and order - (shipped - returned) > tolerance:
            finding('SHIPMENT_INCOMPLETE', refs)
        if any(r.get('inspection_status') in {'REVIEW', 'FAIL'} for r, _, _ in stages['quality_inspection']):
            # Additional to baseline row-specific inspection finding, aggregate is flagged.
            finding('QUALITY_NOT_ALL_PASS', [(r, n) for r, n in refs if r == 'quality_inspection'])
        first_order = min(dated[key]['purchase_order'])
        first_prod = min(dated[key]['production'])
        first_pass = min((parse_date(r['event_date']) for r, _, _ in stages['quality_inspection']
                          if r['inspection_status'] == 'PASS'), default=None)
        if first_prod < first_order:
            finding('PRODUCTION_BEFORE_ORDER', refs)
        if min(dated[key]['quality_inspection']) < first_prod:
            finding('INSPECTION_BEFORE_PRODUCTION', refs)
        if first_pass is None or min(dated[key]['shipment']) < first_pass:
            finding('SHIPMENT_BEFORE_PASSED_INSPECTION', refs)
        # Daily cumulative stage proof. Mere period totals are insufficient: a
        # shipment cannot rely on a subsequent day's passed inspection.
        # Same-day cross-role sequencing lacks times, so it is held for review.
        seen_counts = {'order': Decimal(0), 'new': Decimal(0), 'inspected': Decimal(0),
                       'passed': Decimal(0), 'shipped': Decimal(0), 'returned': Decimal(0)}
        timeline = defaultdict(list)
        for role in ROLES:
            for rec, q, ref in stages[role]:
                timeline[parse_date(rec['event_date'])].append((role, rec, q, ref))
        with localcontext() as ctx:
            ctx.prec = 100
            for current in sorted(timeline):
                prior = seen_counts.copy()
                for role, rec, q, ref in timeline[current]:
                    if role == 'purchase_order':
                        seen_counts['order'] += q
                    elif role == 'production' and rec['movement_kind'] == 'NEW':
                        seen_counts['new'] += q
                        if seen_counts['new'] > prior['order'] + tolerance:
                            finding('TEMPORAL_PRODUCTION_UNSUPPORTED', [ref])
                    elif role == 'quality_inspection':
                        seen_counts['inspected'] += q
                        if rec['inspection_status'] == 'PASS':
                            seen_counts['passed'] += q
                        if seen_counts['inspected'] > prior['new'] + tolerance:
                            finding('TEMPORAL_INSPECTION_UNSUPPORTED', [ref])
                    elif role == 'shipment':
                        if rec['movement_kind'] == 'SHIP':
                            seen_counts['shipped'] += q
                            if seen_counts['shipped'] > prior['passed'] + tolerance:
                                finding('TEMPORAL_SHIPMENT_UNSUPPORTED', [ref])
                        elif rec['movement_kind'] == 'RETURN':
                            seen_counts['returned'] += q
                            if seen_counts['returned'] > prior['shipped'] + tolerance:
                                finding('TEMPORAL_RETURN_UNSUPPORTED', [ref])
        if len(findings) > before:
            flagged_groups += 1

    return findings, {
        'mode': 'FOUR_STAGE_CONSERVATIVE', 'policy_id': policy['policy_id'],
        'policy_version': policy['policy_version'], 'period_start': start.isoformat(),
        'period_end': end.isoformat(), 'groups_checked': len(groups),
        'groups_with_findings': flagged_groups, 'rows_excluded_with_review': invalid,
        'business_meaning': 'Explicit synthetic/customer-approved policy; no quality certification',
    }
