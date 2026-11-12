# SCHEMA — Factory AX 공통 데이터 계약 v0 (설계)
> 2026-11-12 KST · 향후 정식 JSON Schema/OpenAPI/SQLite DDL 작성·테스트 필요. 아래는 **계약 초안**이며 실행 코드가 아니다.

## 1. 기본 원칙
- 모든 객체에 `schema_version`(예: `factoryax.v0`), `source_id`, `rule_set_version`, `artifact_sha256`, `created_at`(오프라인 로컬 timezone 명시), `provenance`를 둔다.
- 고객 민감 원본 값은 기본 감사/외부 공유용 보고서에 넣지 않는다. 내부 UI의 제한된 행 위치 원본 링크는 명시된 역할/권한에서만.
- 이벤트/검수/승인/계획/실행/출력을 별도 자산으로 모델링한다. 실 데이터는 source of truth이며 파생 DB에서 원본 자동 수정 금지.
- 회사별 스키마/프로필의 추정은 사용자가 승인하기 전 `DRAFT`. 유효성 실패·모호성 `REVIEW_REQUIRED`, 외부 권한 실패·변조 `BLOCKED`.

## 2. 최소 객체
### CompanyProfile (고객사 설정)
```json
{
  "schema_version": "factoryax.v0",
  "company_profile_id": "synthetic-company-001",
  "sector": "parts-manufacturing",
  "approved_input_roots": ["C:/FactoryAX/ApprovedExport"],
  "profile_version": "1.0.0",
  "rule_set_version": "rule-set-001",
  "human_approved": false
}
```
- 실제 고객사명/주소/서버 경로·비밀번호는 저장소/문서/테스트에 포함하지 않는다.

### SourceManifest / CanonicalRecord
```json
{
  "schema_version": "factoryax.v0",
  "source_id": "synthetic-purchase-001",
  "dataset_role": "purchase_order",
  "sha256": "64 lowercase hex at runtime, not a sample constant",
  "byte_length": 0,
  "parser_version": "parser-v0",
  "mapping_version": "mapping-v0",
  "source_rows": 0,
  "snapshot_status": "NOT_CAPTURED"
}
```
- `dataset_role`: `purchase_order`, `production`, `quality_inspection`, `shipment`; 이후 승인된 새로운 role만 추가.
- canonical field 후보: `order_id`, `item_id`, `lot_id`, `event_date`, `quantity_decimal`, `quantity_unit`, `inspection_status`, `source_row_number`.
- 유효 행마다 원본 파일 식별/행/열, 파서·매핑 버전. Decimal 기반 정밀 수량, 단위·표준화 규칙 별도.

### ReconciliationPolicy
```json
{
  "schema_version": "factoryax.v0",
  "policy_id": "synthetic-factory-v1",
  "allow_partial_shipment": true,
  "allow_rework": false,
  "lot_join_required": true,
  "unit_conversions_approved": [],
  "unknown_value_policy": "REVIEW_REQUIRED",
  "approved_by": null
}
```
- 주문 1:N, 분할/기간·누계·반품·재작업·불량·폐기 등의 정책을 명시. 프로필에 없는 기본 가정으로 실세계 합격/불합격 판정 금지.

### Finding / Evidence
```json
{
  "schema_version": "factoryax.v0",
  "finding_id": "f-001",
  "finding_code": "QUANTITY_RECONCILIATION_GAP",
  "status": "REVIEW_REQUIRED",
  "severity": "warning",
  "source_refs": [{"source_id":"synthetic-production-001","row":4}],
  "rule_id":"quantity-join-v1",
  "message_ko": "합성 데이터의 정책 확인이 필요합니다."
}
```
- Finding은 근거가 있는 조건 위반/불확실성 표시. `OK`는 검사 범위에 한정하며 안전/품질 인증이 아니다.

### WorkPlan / PolicyDecision / ExecutionReceipt
```json
{
  "schema_version": "factoryax.v0",
  "plan_id": "synthetic-plan-001",
  "action_type": "READ_ONLY_RECONCILE",
  "input_manifest_ids": [],
  "plan_sha256": "runtime sha256",
  "risk_tier": "READ_ONLY",
  "policy_decision": "DENY",
  "reason_code": "HUMAN_APPROVAL_MISSING",
  "approval_id": null,
  "execution_receipt_id": null
}
```
- `policy_decision`: `DENY` / `ALLOW` / `REVIEW_REQUIRED`.
- 변경/외부 전송/삭제·수리·고객 시스템 쓰기에서 새 승인 필수. 승인 상태는 계획 SHA·자산·행위·유효 기간·주체에 결속; 문서 위조로 자동 승인 불가.
- HAE 계획과 LA 실행 영수증은 서로 다른 신뢰 계층. SOVIA는 감사/불일치 관측 결과일 뿐 인증/권한의 단독 근거가 아니다.

### EndpointDiagnostic / CodeFinding
- EndpointDiagnostic: `host_asset_id`, `snapshot_time`, `check_id`, `measured_value`(사내 최소화), `threshold_version`, `read_only_confirmed`, `schedule_id`(선승인된 경우), `status`.
- CodeFinding: `approved_source_manifest`, `rule_code`, `language`, `source_line`, `confidence_kind`(heuristic/verified), `false_positive_review`, `scope_limit`.
- 코드 정적 분석 결과만으로 실행 승인/보안 인증/악성코드 부재 확인하지 않는다.

## 3. 저장·복구
- `assets`, `mappings`, `rule_sets`, `runs`, `findings`, `approvals`, `policy_decisions`, `step_receipts`, `reports`, `backup_manifests`, `diagnostics`는 스키마/마이그레이션 계약을 가진 논리 테이블.
- 데이터 단위 테스트와 재현용 테스트 fixture는 모두 **합성**. 실제 저장·DDL은 W1 구현 시 테스트 증거와 함께 확정.
