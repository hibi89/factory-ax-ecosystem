> **feature/data-verify 2026-11-12:** First executable Factory VERIFY **W1 50% provisional engineering** milestone, limited synthetic CSV/XLSX quality and reports. Original main design-only baseline preserved, entire Factory Ecosystem **UNASSESSED**, commercial **RELEASE HOLD**. See [VERIFY_README.md](VERIFY_README.md) and [checkpoint evidence](docs/VERIFY_50_EVIDENCE_20261112.md).

# Factory AX Ecosystem
> **Private · design baseline 2026-11-12 KST · NOT BUILT / RELEASE HOLD**

**Factory AX**는 보수적인 한국 제조업·일반 기업의 기존 설비/ERP/MES를 교체하지 않고, 승인된 업무 PC·폐쇄망에서 Excel/CSV/문서/파일을 **검수→근거화→업무화→승인형 자동화**하는 **표준제품 기반 구축·납품(Productized Implementation)** 생태계다.

## 사업 정체성
- **고객은 완성된 납품 프로그램을 사용한다.** 고객에게 SMAX² SELF 플랫폼에서 직접 구축하라고 요구하지 않는다.
- **우리(공급자)**가 고객별로 정해진 범위의 템플릿/열 매핑/정책을 설정·시험·납품한다. 고객별 무제한 SI/ERP 교체와 구분한다.
- **SMAX²는 별도 범용 셀프서비스 플랫폼**이다. Factory AX는 기존 SMAX² **PREP의 데이터 계약/검증된 기술만 허가·호환성 검사 후 재사용**한다.
- 첫 상품은 **Factory AX VERIFY**(발주·생산·품질·출하 Excel/CSV 대사). 장기 최종 목표는 **HAE + Lightning Azent(LA)를 중심**으로 내부 업무·문서·파일·데이터·보안 감사·PC 건강 상태를 통합하는 **고객 승인형 온프레미스 AX 운영체계**다.
- **최초부터 폐쇄망 100% 안전, 전 NAS 호환, AI 무오류, 절반 인건비 절감, 무인 수리, 방산 인증 등을 주장하지 않는다.** 보안·가용성·정확도는 고객 환경 시험으로 증명해야 한다.

## 최종 제품 포트폴리오
| 단계 | 제품/모듈 | 고객이 실제로 얻는 것 | 현재 |
|---|---|---|---|
| W1 진입 | **Factory AX CORE + VERIFY** | 고객 양식 매핑, LOT/품목/수량 대조, 누락·중복 검출, 원문 행 근거·보고서 | 설계만 |
| W2 확장 | **KNOWLEDGE** | 매뉴얼·작업표준서 로컬 검색, 출처·페이지 표시, 불확실 답변 보류 | 설계만 |
| W2 확장 | **FILE** | 검사성적서·도면·납품 폴더/SMB 읽기 전용 검수 | 설계만 |
| W3 AX화 | **HAE + LA AUTOMATION** | 고객 승인 워크플로, 스케줄·재시도·체크포인트·감사 | 별도 원천 기술만 |
| W4 보안 | **SECURITY + SOVIA** | 정책 기반 실행 차단, 승인 기록·감사, 오프라인 보안 근거 | 일부 별도 기술/신규 개발 |
| W4 운영 | **ENDPOINT CARE + CODE QA** | 일반 업무용 Windows PC 읽기 전용 진단·정기 점검·승인된 소스 정적 검토 | 원천 알파/별도 검토 |
| 장기 | **Factory AX Control Console** | 자산·작업·근거·보고·복구·확장 모듈 통합 | 설계만 |

**상용 출시 상태: 전체 RELEASE HOLD.** 이번 저장소 초기화는 문서/브랜치 설정이지 제품 구현, 실고객 설치, 폐쇄망 인증, 실거래가 아니다.

## 지금부터 읽는 순서
1. [START_HERE.md](START_HERE.md) — 새 채팅·총괄 즉시 복원
2. [HANDOFF.md](HANDOFF.md) → [STATUS.md](STATUS.md) — 최신 중단 지점과 증거
3. [AGENTS.md](AGENTS.md) → [REQUIREMENTS.md](REQUIREMENTS.md) — 원칙/요구사항
4. [docs/PRODUCT_BLUEPRINT.md](docs/PRODUCT_BLUEPRINT.md) — **최종 100% 제품 정의**
5. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [SCHEMA.md](SCHEMA.md) — 기술 경계
6. [docs/BRANCH_STRATEGY.md](docs/BRANCH_STRATEGY.md), [docs/ROADMAP.md](docs/ROADMAP.md) — 분야별 브랜치와 순서
7. [docs/ACCEPTANCE_MATRIX.md](docs/ACCEPTANCE_MATRIX.md) — 검증 기준/출시 게이트
8. [docs/SOURCE_REUSE_MATRIX.md](docs/SOURCE_REUSE_MATRIX.md) — 원천 GitHub 재사용 출처와 제약
9. [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md), [docs/COMMERCIAL_MODEL.md](docs/COMMERCIAL_MODEL.md), [docs/OPERATIONS.md](docs/OPERATIONS.md).

## 운영 요약
- 소스·버전 정본: **`hibi89/factory-ax-ecosystem` (Private)**. 타 제품/해커톤/고객 자료는 **여기에서 임의로 복제·변경하지 않는다**.
- `main` 승인된 안정 기준, `integration/develop` 통합, 기능별 `feature/*` 개발. 현재는 문서만 담으며 별도 제품 코드/실행 명령·Production URL은 없다.
- 외부 고객 데이터/API 키/민감정보와 보안 설정, 지출·외부 전송·공개 배포/실고객 시스템 연결은 **명시 승인 전 금지**.
- 목표는 **월 필수 클라우드·LLM API·서버 구독 0원**인 로컬/온프레미스 제품. 고객 PC·장비·지원·유지보수·세금·판매 수수료까지 0원 보장은 아니다.
- 사용자 `ㄱ` 지시는 최신 GitHub 지침과 HEAD 확인 후 해당 범위의 **다음 검증 가능한 실제 작업 1단위 수행**을 의미한다.

_이 문서가 있더라도 미생성 연결 문서는 초기 트리 준비가 끝난 뒤에 유효하다._
