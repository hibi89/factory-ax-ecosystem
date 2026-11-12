# Factory AX 시험·검증 전략
> 현재 실행된 Factory AX 단위/통합/브라우저/Windows/고객 테스트는 **0건**.

## 1. 검증 원칙
- 테스트 등록/과거 타 레포 CI/합성 예상값은 새 제품 통합 성공이 아니다.
- 새 제품에서 실제 명령·원격 커밋 SHA·PASS/FAIL/SKIP·OS·네트워크·자료 유형을 정확히 남긴다.
- 처음에는 합성 허구 공장 데이터만 사용. 고객 보안자료는 고객 내부 승인 환경, 비공개 데이터 계약과 접근 통제 후에만.

## 2. 층별 시험 계획
1. **Contract/Schema**: DataManifest/CanonicalRecord/ReconciliationPolicy/Findings/Plan/Consent/Receipt JSON schema, 숫자 Decimal·단위/키/일자/프로필 버전.
2. **Pure domain**: order vs production vs inspection vs shipment 독립 reference oracle, 불일치/중복/부분 출하/재작업/확인 불가 상태.
3. **Ingestion**: CSV UTF-8/BOM, XLSX 여러 시트/수식·매크로·행 제한, file change and unlink, symlink/junction, 상대/절대/UNC, 경로 이탈·대용량/빈 파일.
4. **Security**: origin/localhost, OS ACL/경로 거부·민감 로그/외부 호출 0, injection and poisoned doc, 정책/승인 위조, 비인가 write denied.
5. **Storage/recovery**: idempotency, interruption, new-only report, atomic staging/crash, SQLite WAL/restore, schema upgrade/downgrade/rollback.
6. **UI/browser**: real Windows 10/11 Chrome/Edge (해당되는 경우), keyboard focus, 한글 PDF/Excel/csv formula escaping, error states, customer wizard.
7. **Installation**: Windows clean machine, antivirus/SmartScreen behavior, version update/uninstall/reinstall, offline no npm/pip runtime required, SBOM/NOTICE.
8. **Integrations later**: actual HAE↔LA with Guard/SOVIA/DBVORA process boundary, read-only SMB/Q&A/PC CARE, negative/positive replay and audits.
9. **Customer**: 사용자가 승인한 데이터와 실제 업무담당자 참여, 결과의 정답·원본/설비 불변 및 유료 가치·작업시간 실측.

## 3. W1 최소 synthetic fixture 설계
- `purchase.csv`: order_id, item_id, order_qty, unit, due_date.
- `production.csv`: order_id, item_id, lot_id, production_date, produced_qty, unit.
- `inspection.csv`: lot_id, item_id, inspected_qty, accepted_qty, rejected_qty, status, inspection_date.
- `shipment.csv`: order_id, item_id, lot_id, shipment_qty, unit, shipment_date.
- 케이스: 정상, 부분 생산, 분할 출하, 생산/검사 일부 불량, 중복 송장/LOT, 일자·단위 불일치, 잘못된 품목/키, 누락 필수열, 재검·반품, 파일 중간 변조.
- 모든 합성 fixture는 해당 정답(합계·원본 위치·finding code·REVIEW/BLOCKED 조건)과 독립 validator를 갖춘다.

## 4. 첫 코드 개발 후 명령 제안(아직 미구현)
```text
python -m pytest -q
python -m factoryax verify --config examples/synthetic/profile.json --input-dir examples/synthetic --dry-run
python scripts/verify_offline_bundle.py <path>
```
**위 명령은 미래의 실행 인터페이스 후보이며 지금 실행할 수 없다.** 실제 프로젝트 레이아웃과 테스트 명령은 첫 코드 커밋에서 정하고 인수 문서에 새 근거를 올린다.

## 5. CI/배포
- Linux/Python3.11+ 기본→Windows GitHub-hosted→실 구매자 Windows10/11 차례로 통과해야 한다.
- 기본적으로 Vercel/Cloudflare/온라인 API/Production은 **미적용**.
- W3 이후 Guard 실행/스케줄/보안 프로세스에 fault injection과 system resource monitoring 필수.
