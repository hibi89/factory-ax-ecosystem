# 통합 책임·인터페이스 계약 (설계 v0)
> 프로토타입 실행 코드 없음. 원천 제품을 직접 import/copy하는 계약이 아니다.

## 1. 계약 기준
- 모든 외부 모듈은 `version + bounded input + provenance + explicit consent + result + warnings/errors` 계약을 갖는다.
- 실행권한은 Plan/LLM/문서 검색이 아니라 **독립 Guard 및 OS 최소권한**이 부여한다.
- 데이터를 내보내는 계층마다 손실·누락·금액/수량 변환/원본 행 근거를 확인한다. 고객 원본은 결코 내부 규칙의 source of truth로 무단 교체하지 않는다.

## 2. Interface catalog
| ID | Producer -> Consumer | 입력 -> 출력 | 보안/재시도 |
|---|---|---|---|
| I-01 | Customer approved source -> CORE | 허용 폴더 + SourceManifest -> immutable snapshot receipt | bounds/sha/reparse/lock/ACL |
| I-02 | PREP-equivalent -> EAI | CompanyProfile+Mapping+raw typed records -> CanonicalRecord/ReviewQueue | unmapped or ambiguous -> REVIEW |
| I-03 | EAI -> VERIFY | Canonical 4-table + ReconciliationPolicy -> Findings+Evidence | no original writes; Decimal/referential integrity |
| I-04 | FlowPilot -> CORE/FILE | approved path manifest -> file completeness/sha/version evidence | SMB read-only; access lost -> HOLD |
| I-05 | RAG -> KNOWLEDGE | owner-approved document manifests/query -> cited source results | ACL/source version and prompt injection isolation |
| I-06 | HAE -> Security Guard | typed plan SHA+subject+asset+action -> allow/deny/need approval | not executable before policy decision |
| I-07 | Guard -> LA | time-bound minimal capability+plan SHA -> execution receipt | revalidation every run; no raw secret |
| I-08 | LA -> SOVIA | minimized plan/observations -> advisory audit findings | SOVIA is not a policy issuer |
| I-09 | DBVORA -> HAE/console | approved DB schema/snapshot/restore attest -> read-only asset status | DBVORA read/backup separate from business write |
| I-10 | PC CARE -> console | signed/validated local diagnostic summary -> trend/alert | client authorized, read-only, no OT |
| I-11 | CodeChecker -> console | approved code manifest -> static findings/rule scope | no arbitrary source submission/execution |

## 3. 상태 전이
- `INPUT_PENDING` → `PREFLIGHT_OK` / `BLOCKED`
- `PREFLIGHT_OK` → `REVIEW_REQUIRED` / `READY_FOR_REVIEW`
- `READY_FOR_REVIEW` → `APPROVED` / `REJECTED`; 승인 시 source/plan/profile/rule SHA 바인딩.
- `APPROVED` + Guard allow → `RUNNING` → `COMPLETED` or `FAILED/HOLD`; 시간 초과/외부 변경 시 새 승인 또는 재검사.
- 자동 치료·시스템 재시작·타 고객 계정·원격 데이터 전송은 초기 스키마에서 `DENY`한 작업 종류.

## 4. 마이그레이션·인수
- 변경 없는 버전 호환성 표·fixture와 source SHA, NEGATIVE 테스트 우선.
- I-01~03=W1 우선. I-04/05=W2, I-06~09=W3, I-10/11=W4. 단, W1의 최소 정책/파일 보안은 필수.
- 각 인터페이스는 별도 acceptance owner, failure mode, rollback/restore, backward-compatibility tests를 확보.
