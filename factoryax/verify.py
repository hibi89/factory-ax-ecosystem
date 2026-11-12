"""Local read-only factory CSV/XLSX validation; no code copied from PREP/EAI.

Input is an explicitly approved, SHA-pinned specification. This is a limited
W1 50%-gate core, not a complete manufacturing quality certification system.
"""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from zipfile import ZipFile, BadZipFile

SCHEMA = 'factoryax.v0'
ROLES = ('purchase_order', 'production', 'quality_inspection', 'shipment')
COMMON = ('record_id', 'order_id', 'item_id', 'lot_id', 'quantity', 'unit')
REQUIRED = {r: COMMON + (('inspection_status',) if r == 'quality_inspection' else ()) for r in ROLES}
EXTRAS = {r: ('event_date',) + (('movement_kind',) if r in ('production', 'shipment') else ()) for r in ROLES}
MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 10000
MAX_COLS = 80
MAX_ZIP_UNCOMPRESSED = 12 * 1024 * 1024
ALLOWED_ZIP = re.compile(r'^(\[Content_Types\]\.xml|_rels/\.rels|docProps/(app|core)\.xml|xl/(workbook\.xml|_rels/workbook\.xml\.rels|styles\.xml|sharedStrings\.xml|worksheets/sheet1\.xml))$')
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
XLNS = '{' + NS['m'] + '}'
HEX64 = re.compile(r'^[a-f0-9]{64}$')


class IntakeError(Exception):
    """Fail closed on unsafe/ambiguous input: BLOCKED, no report output."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _safe_path(root, filename):
    """Reject traversal, UNC, symlinks/junctions and non-regular files."""
    if not isinstance(filename, str) or not filename or '\\' in filename:
        raise IntakeError('PATH_INVALID')
    relative = Path(filename)
    if relative.is_absolute() or '..' in relative.parts or '.' in relative.parts:
        raise IntakeError('PATH_OUTSIDE_APPROVED_ROOT')
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise IntakeError('APPROVED_ROOT_INVALID')
    root = root.resolve(strict=True)
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise IntakeError('SYMLINK_DENIED')
        if os.name == 'nt':
            attrs = getattr(candidate.lstat(), 'st_file_attributes', 0)
            if attrs & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
                raise IntakeError('REPARSE_POINT_DENIED')
    try:
        if os.path.commonpath((str(root), str(candidate.resolve(strict=True)))) != str(root):
            raise IntakeError('PATH_OUTSIDE_APPROVED_ROOT')
        if not candidate.is_file():
            raise IntakeError('NOT_REGULAR_FILE')
    except (OSError, ValueError) as exc:
        raise IntakeError('INPUT_UNAVAILABLE') from exc
    return candidate


def _read_exact(path, expected_sha):
    if not isinstance(expected_sha, str) or not HEX64.fullmatch(expected_sha):
        raise IntakeError('SOURCE_SHA_REQUIRED')
    try:
        before = path.stat()
        if before.st_size > MAX_BYTES or before.st_size == 0:
            raise IntakeError('SIZE_OUT_OF_BOUNDS')
        # O_NOFOLLOW protects the leaf on POSIX; ancestor changes remain a known limitation.
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        try:
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise IntakeError('SOURCE_CHANGED')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                data = stream.read(MAX_BYTES + 1)
            after_open = os.fstat(fd)
        finally:
            os.close(fd)
        after = path.stat()
    except OSError as exc:
        raise IntakeError('INPUT_READ_FAILED') from exc
    if (len(data) != opened.st_size or len(data) > MAX_BYTES or
        (before.st_size, before.st_mtime_ns, before.st_ino, before.st_dev) !=
        (after.st_size, after.st_mtime_ns, after.st_ino, after.st_dev) or
        (opened.st_size, opened.st_mtime_ns) != (after_open.st_size, after_open.st_mtime_ns)):
        raise IntakeError('SOURCE_CHANGED')
    sha = digest(data)
    if sha != expected_sha:
        raise IntakeError('SOURCE_SHA_DRIFT')
    return data, sha


def _csv_rows(data):
    if b'\x00' in data:
        raise IntakeError('CSV_NULL_BYTE')
    try:
        content = data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise IntakeError('CSV_UTF8_REQUIRED') from exc
    reader = csv.reader(io.StringIO(content, newline=''), strict=True)
    try:
        rows = list(reader)
    except csv.Error as exc:
        raise IntakeError('CSV_MALFORMED') from exc
    if not rows or len(rows) > MAX_ROWS + 1 or any(len(row) > MAX_COLS for row in rows):
        raise IntakeError('CSV_SIZE_LIMIT')
    return [(index + 1, row) for index, row in enumerate(rows)]


def _xlsx_rows(data):
    if not data.startswith(b'PK\x03\x04'):
        raise IntakeError('XLSX_MAGIC_INVALID')
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            if not infos or len(infos) > 25 or len({x.filename for x in infos}) != len(infos):
                raise IntakeError('XLSX_ZIP_ENTRIES')
            if any(not ALLOWED_ZIP.fullmatch(x.filename) or x.flag_bits & 1 or x.file_size > MAX_ZIP_UNCOMPRESSED
                   or (x.compress_size and x.file_size > x.compress_size * 150) for x in infos):
                raise IntakeError('XLSX_UNSAFE_CONTENT')
            if sum(x.file_size for x in infos) > MAX_ZIP_UNCOMPRESSED:
                raise IntakeError('XLSX_TOO_LARGE')
            for required in ('xl/workbook.xml', 'xl/worksheets/sheet1.xml'):
                if required not in archive.namelist():
                    raise IntakeError('XLSX_SHEET_MISSING')
            def load_xml(member):
                raw = archive.read(member)
                if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
                    raise IntakeError('XLSX_XML_ENTITY')
                return ET.fromstring(raw)
            book = load_xml('xl/workbook.xml')
            sheets = book.findall('m:sheets/m:sheet', NS)
            if len(sheets) != 1 or sheets[0].get('state', 'visible') != 'visible':
                raise IntakeError('XLSX_SINGLE_VISIBLE_SHEET_ONLY')
            strings = []
            if 'xl/sharedStrings.xml' in archive.namelist():
                shared = load_xml('xl/sharedStrings.xml')
                strings = [''.join(x.text or '' for x in si.findall('.//m:t', NS)) for si in shared.findall('m:si', NS)]
            sheet = load_xml('xl/worksheets/sheet1.xml')
            if sheet.findall('.//m:f', NS):
                raise IntakeError('XLSX_FORMULA_DENIED')
            rows = []
            for row in sheet.findall('m:sheetData/m:row', NS):
                rn = int(row.get('r', '0'))
                if rn < 1 or rn > MAX_ROWS + 1:
                    raise IntakeError('XLSX_ROW_RANGE')
                vals = {}
                for cell in row.findall('m:c', NS):
                    ref = cell.get('r', '')
                    match = re.fullmatch(r'([A-Z]{1,3})([1-9]\d*)', ref)
                    if not match or int(match.group(2)) != rn:
                        raise IntakeError('XLSX_CELL_REF')
                    col = 0
                    for char in match.group(1):
                        col = col * 26 + ord(char) - 64
                    if col > MAX_COLS or col in vals:
                        raise IntakeError('XLSX_COLUMN_RANGE')
                    typ = cell.get('t', 'n')
                    node = cell.find('m:v', NS)
                    if typ == 'inlineStr':
                        val = ''.join(n.text or '' for n in cell.findall('.//m:t', NS))
                    elif typ == 's':
                        idx = int(node.text if node is not None and node.text is not None else '-1')
                        if idx < 0 or idx >= len(strings):
                            raise IntakeError('XLSX_SHARED_STRING_INDEX')
                        val = strings[idx]
                    elif typ in ('str', 'n', 'b'):
                        val = (node.text or '') if node is not None else ''
                    else:
                        raise IntakeError('XLSX_CELL_TYPE')
                    vals[col] = val
                rows.append((rn, [vals.get(i, '') for i in range(1, max(vals, default=0) + 1)]))
            if not rows or rows[0][0] != 1 or len(rows) > MAX_ROWS + 1:
                raise IntakeError('XLSX_ROWS_INVALID')
            return rows
    except (BadZipFile, ET.ParseError, ValueError, KeyError, OverflowError, RuntimeError) as exc:
        raise IntakeError('XLSX_PARSE_FAILED') from exc


def _as_records(data, extension, mapping, role, source_id, findings):
    rows = _csv_rows(data) if extension == '.csv' else _xlsx_rows(data)
    headers = rows[0][1]
    if not headers or len(headers) != len(set(headers)) or any(not h or not h.strip() for h in headers):
        raise IntakeError('HEADERS_INVALID')
    if not set(REQUIRED[role]).issubset(mapping) or not set(mapping).issubset(set(REQUIRED[role]) | set(EXTRAS[role])) or any(not isinstance(v, str) or v not in headers for v in mapping.values()):
        raise IntakeError('MAPPING_UNAPPROVED_OR_MISSING')
    if len(set(mapping.values())) != len(mapping.values()):
        raise IntakeError('MAPPING_DUPLICATE_COLUMN')
    indexes = {key: headers.index(original) for key, original in mapping.items()}
    records = []
    for row_number, row in rows[1:]:
        if len(row) > len(headers) or (any(c.strip() for c in row) and len(row) < len(headers)):
            findings.append(_finding('ROW_COLUMN_COUNT', source_id, row_number))
        if not any(x.strip() for x in row):
            continue
        record = {key: row[index].strip() if index < len(row) else '' for key, index in indexes.items()}
        record['_source'] = source_id
        record['_row'] = row_number
        records.append(record)
    return records, len(rows) - 1


def _finding(code, source_id, row, severity='REVIEW_REQUIRED'):
    return {'code': code, 'status': severity, 'source_refs': [{'source_id': source_id, 'row': row}]}


def _validate(spec):
    if not isinstance(spec, dict) or spec.get('schema_version') != SCHEMA or spec.get('human_approved') is not True:
        raise IntakeError('APPROVED_SPEC_REQUIRED')
    if not isinstance(spec.get('profile_version'), str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,40}', spec['profile_version']):
        raise IntakeError('PROFILE_VERSION_REQUIRED')
    if not isinstance(spec.get('rule_set_version'), str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,40}', spec['rule_set_version']):
        raise IntakeError('RULE_VERSION_REQUIRED')
    if set(spec.get('files', {})) != set(ROLES):
        raise IntakeError('FOUR_ROLES_REQUIRED')
    if not isinstance(spec.get('approved_root'), str):
        raise IntakeError('APPROVED_ROOT_REQUIRED')
    units = spec.get('approved_units')
    if not isinstance(units, list) or not units or any(not isinstance(u, str) or not re.fullmatch(r'[A-Z]{1,6}', u) for u in units):
        raise IntakeError('APPROVED_UNITS_REQUIRED')
    if len(set(units)) != len(units):
        raise IntakeError('DUPLICATE_UNIT')
    return units


def verify(spec):
    units = _validate(spec)
    findings, manifests, records = [], [], {}
    filenames = []
    for role in ROLES:
        info = spec['files'][role]
        if not isinstance(info, dict) or not all(k in info for k in ('path', 'sha256', 'mapping')):
            raise IntakeError('FILE_ENTRY_REQUIRED')
        file = info['path']
        if file in filenames:
            raise IntakeError('FILE_ROLE_COLLISION')
        filenames.append(file)
        path = _safe_path(spec['approved_root'], file)
        ext = path.suffix.lower()
        if ext not in ('.csv', '.xlsx'):
            raise IntakeError('EXTENSION_NOT_ALLOWED')
        data, sha = _read_exact(path, info['sha256'])
        if ext == '.csv' and data.startswith(b'PK'):
            raise IntakeError('FORMAT_MISMATCH')
        source_id = role  # no input paths/customer values in the report
        rec, row_count = _as_records(data, ext, info['mapping'], role, source_id, findings)
        manifests.append({'source_id': source_id, 'role': role, 'sha256': sha, 'bytes': len(data),
                          'source_rows': row_count, 'mapping_version': spec['profile_version']})
        records[role] = rec
    seen = set()
    ordered = {}
    for role in ROLES:
        for rec in records[role]:
            src, row = rec['_source'], rec['_row']
            for field in REQUIRED[role]:
                if not rec[field]:
                    findings.append(_finding('MISSING_REQUIRED_' + field.upper(), src, row))
            unique = (role, rec['record_id'])
            if unique in seen and rec['record_id']:
                findings.append(_finding('DUPLICATE_RECORD_ID', src, row))
            seen.add(unique)
            if rec['unit'] not in units:
                findings.append(_finding('UNAPPROVED_UNIT', src, row))
            try:
                number = Decimal(rec['quantity'])
                if not number.is_finite() or number <= 0:
                    raise InvalidOperation()
            except (InvalidOperation, ValueError):
                findings.append(_finding('INVALID_QUANTITY', src, row))
            if role == 'quality_inspection':
                if rec['inspection_status'] not in ('PASS', 'FAIL', 'REVIEW'):
                    findings.append(_finding('UNKNOWN_INSPECTION_STATUS', src, row))
                elif rec['inspection_status'] != 'PASS':
                    findings.append(_finding('INSPECTION_NOT_PASS', src, row))
            key = (rec['order_id'], rec['item_id'], rec['lot_id'])
            if role == 'purchase_order' and all(key):
                ordered[key] = True
    for role in ROLES[1:]:
        for rec in records[role]:
            key = (rec['order_id'], rec['item_id'], rec['lot_id'])
            if all(key) and key not in ordered:
                findings.append(_finding('ORPHAN_ORDER_ITEM_LOT', role, rec['_row']))
    reconciliation = None
    if 'reconciliation_policy' in spec:
        from .reconcile import ReconciliationError, reconcile
        try:
            extra_findings, reconciliation = reconcile(spec, records, units)
        except ReconciliationError as exc:
            raise IntakeError(str(exc)) from exc
        findings.extend(extra_findings)
    report = {'schema_version': SCHEMA, 'product': 'Factory AX VERIFY',
              'scope': ('W1-70: conservative four-stage reconciliation' if reconciliation else 'W1-50: input integrity + quality checks only; NOT full four-stage reconciliation'),
              'status': 'REVIEW_REQUIRED' if findings else 'OK',
              'profile_version': spec['profile_version'], 'rule_set_version': spec['rule_set_version'],
              'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'manifests': manifests, 'record_counts': {r: len(records[r]) for r in ROLES},
              'reconciliation': reconciliation,
              'findings': findings, 'quality_rule_families': ['required', 'uniqueness', 'unit_and_decimal', 'reference_integrity', 'inspection_status']}
    return report


def export_new(report, out):
    out = Path(out).absolute()
    if out.exists():
        raise IntakeError('OUTPUT_EXISTS_NO_OVERWRITE')
    if not out.parent.is_dir() or out.parent.is_symlink():
        raise IntakeError('OUTPUT_PARENT_INVALID')
    stage = Path(tempfile.mkdtemp(prefix='.factoryax-stage-', dir=out.parent))
    try:
        (stage / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        with (stage / 'summary.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['dataset_role', 'source_rows', 'sha256'])
            for item in report['manifests']:
                writer.writerow([item['role'], item['source_rows'], item['sha256']])
        rows = ''.join('<tr><td>' + html.escape(x['role']) + '</td><td>' + str(x['source_rows']) +
                       '</td><td><code>' + x['sha256'] + '</code></td></tr>' for x in report['manifests'])
        out_html = ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" '
                    'content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;">'
                    '<title>Factory AX VERIFY - 합성/승인 자료 검수</title><style>body{font:16px system-ui;'
                    'max-width:960px;margin:3rem auto;padding:1rem}td,th{border-bottom:1px solid #aaa;'
                    'padding:10px;text-align:left;overflow-wrap:anywhere}table{width:100%}</style><h1>Factory AX VERIFY</h1>'
                    '<p>승인된 범위의 제한적 입력·대사 검수입니다. 제품 적합/품질 인증이 아닙니다.</p><p>결과: <strong>' +
                    html.escape(report['status']) + '</strong>; 추가 확인 항목: ' + str(len(report['findings'])) +
                    '</p><table><thead><tr><th>유형</th><th>행</th><th>SHA-256</th></tr></thead><tbody>' + rows +
                    '</tbody></table><p>근거 상세는 내부 제한 보관 result.json을 확인하세요. 원본 값은 이 보고서에 포함하지 않습니다.</p></html>')
        (stage / 'summary.html').write_text(out_html, encoding='utf-8')
        for name in ('result.json', 'summary.csv', 'summary.html'):
            with (stage / name).open('rb') as stream:
                os.fsync(stream.fileno())
        os.rename(stage, out)  # destination must not preexist; platform-specific concurrent race remains.
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description='Factory AX offline VERIFY; approved four-file synthetic/authorized input only')
    parser.add_argument('--spec', required=True, help='Local explicit approval spec (JSON)')
    parser.add_argument('--output', required=True, help='New, nonexisting report directory')
    args = parser.parse_args(argv)
    try:
        spec = json.loads(Path(args.spec).read_text(encoding='utf-8'))
        report = verify(spec)
        export_new(report, args.output)
        print(json.dumps({'status': report['status'], 'findings': len(report['findings']),
                          'output': str(Path(args.output).absolute())}, ensure_ascii=False))
        return 0 if report['status'] == 'OK' else 2
    except (IntakeError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        # no source path or original contents printed
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc) if isinstance(exc, IntakeError) else 'INVALID_INPUT_OR_IO'}))
        return 3
