# 2026-11-12 KST — Main CI manual native Windows GUI gate
- Owner-approved default-branch CI registration preserved; added Windows native Tk synthetic widget step. No product sources merged, no auto-trigger, runner execution/billing, customer data or external API. Main remains baseline.
- Current Factory feature source `f3e2649c49a73c2621180bab115d30ef4a16ea1b` has source-only Windows one-click QA. Local split-suite 134 PASS; actual Windows CMD/Tk/CI **not run**, score 82 provisional and RELEASE HOLD. Full 10-point product handoff on `feature/data-verify/HANDOFF.md`.
- To proceed: inspect account Actions usage/budgets and manually dispatch feature workflow, or run `RUN_FACTORYAX_WINDOWS_QA.cmd` from verified source ZIP on owner ordinary Windows. GitHub main latest SHA read after write; revert without force.

# 2026-11-12 KST — Main CI registration update
- With owner's explicit approval, main only registered a manual-only, synthetic, read-only Windows/Linux QA workflow (`.github/workflows/verify-owner-qa.yml`). Registration SHA: `f54b74ebc5bd838c2305ae18672750fbad87ba4b`. The job executes only when explicitly dispatched against `feature/data-verify`; no automatic runs and total history still 0 at inspection.
- **Main remains a design/document baseline**, no product logic merged. Actual 82% provisional W1 code and 120 local tests are on `feature/data-verify`, 85 and native Windows/CI unverified; Factory entire ecosystem UNASSESSED. Read feature branch HANDOFF first for current product details; account billing usage/budget must be checked before manual dispatch. All releases HOLD.
- No other original branches, repos, production, customer files or credentials changed. Latest main SHA is obtained by ref query after this documentation commit. Revert this note/workflow through Git history if needed, no force.

# HANDOFF — Factory AX Ecosystem 총괄 인수인계 (필수 10항)
> 갱신 기준: **2026-11-12 KST**, 첫 Private 저장소 구조/문서 구성. 새 채팅은 정확한 GitHub 최신 HEAD부터 재조회.

1. **목표·용도·확정 요구·기술:** `hibi89/factory-ax-ecosystem`(Private)에서 제조업/보수적 기업 공급자 납품형 온프레미스 AX 운영체계 개발. W1 **CORE+VERIFY**(PREP 계약·EAI 품질, 4종 제조 Excel/CSV)로 진입, W2 RAG/FILE, W3 **HAE+LA** 승인형 내부 AX, W4 SOVIA+Guard 보안·PC CARE 정기 읽기 점검·Code Checker·Control Console 장기 통합. SMAX²는 별도 SELF 플랫폼, PREP만 재사용 후보.
2. **완료 기능/변경·결정 근거:** 사용자 생성 빈 Private repo에 전체 최종 설계·전략·README/START/AGENTS/REQUIREMENTS/SCHEMA, 아키텍처·원천재사용·브랜치·로드맵·기능별 작업 지침·보안/운영/상업/인수 기준·진척표 문서를 기록. 공급자 표준제품 구축 vs 맞춤 SI/고객 SELF 비교 후 납품형 선택, Python 1런타임+버전형 어댑터는 추천 설계(이식/성능 검증 전), 고위험 자동화 금지.
3. **테스트 명령·성공/실패·미검증:** 이번에는 제품 코드/테스트/빌드/CI **실행 0 / PASS 0 / FAIL 0 / SKIP 0**. GitHub 원격 문서/브랜치/커밋 확인은 작업 종료 시 수행. 원천 HAE/EAI/SMAX/UGREEN 합성 CI는 새 Factory 제품 기능 테스트가 아님. 사용자 Windows/OT/고객 파일/네트워크 차단/installer 모두 미검증.
4. **완료/진행/대기/차단:** 저장소 문서/브랜치 초기화가 이 단계의 완료 목표. W1 전체 구현부터 고객 파일럿/판매, W2~W4 실제 통합은 대기. **Factory 기능 완성률 미측정; 모든 제품 RELEASE HOLD**.
5. **오류·근거·시도·재시도 금지·대안:** 초기 repo는 파일 없는 정상 빈 저장소(README 404/branches[]), 앱 장애 아님. 기존 HAE 전체 CI 패키지/source parity 잔여 2 FAIL과 UGREEN NAS 실기기·PC CARE Win실기기 미검증. 자료 규칙 불확실하면 REVIEW, 외부 권한/해시/원본 드리프트 BLOCKED. 원본 무단 복사·과거 실패 skip/무의미한 재실행 금지.
6. **저장소·브랜치·SHA·경로:** `hibi89/factory-ax-ecosystem`, `main` 안정, `integration/develop` 통합, `feature/data-verify`, `feature/knowledge-rag`, `feature/file-nas`, `feature/hae-la`, `feature/security-governance`, `feature/endpoint-codeqa`, `feature/control-console`, `feature/delivery-ops` 분할. 각각 같은 문서 기준점부터 생성. 정확한 최신 SHA는 GitHub 브랜치 HEAD 재조회(문서 커밋과 자기 자신 SHA 동시 고정 불가). 경로 `docs/PRODUCT_BLUEPRINT.md`, `docs/BRANCH_STRATEGY.md`, `docs/ACCEPTANCE_MATRIX.md`, `docs/workstreams/*`.
7. **Production URL·Vercel/실행 명령·환경:** **현재 미적용**. 새로운 실행 가능 소스 없음. W1 계획 Python3.11+ Windows 로컬 GUI/CSV/XLSX/SQLite, 실제 기술/명령은 첫 코드 커밋 뒤 확정. 외부 SaaS/API/유료 LLM 필수 X가 목표.
8. **원본 위치·백업·인증/수정 금지:** 기존 SMAX², EAI, HAE/LA, SOVIA, DBVORA, RAG, UGREEN, AX_MART PC CARE, Code Checker 원본 저장소/브랜치·고객자료/비밀·해커톤 제출물 보존·미수정. Private GitHub 이력/초기 commit으로 문서 복구 가능. 로컬 실고객/보안 자료는 GitHub/모델/외부로 업로드 금지. 고객 비밀/환경변수 없음.
9. **다음 작업 우선순위·절차·완료 기준·승인:** (1) 원천 PREP/EAI 최신 HEAD/사용권 검토→(2) 제조업 4파일 합성 정답 fixture·계약/보안→(3) `feature/data-verify` 최소 Python CORE/EAI/제조대사 실제 코드·테스트→(4) 검수 UI/오프라인 Windows 패키지→(5) 실고객 인수/권리/가격 실증. 변경/고객 접근/소스 이식/배포/지출/보안설정은 사전 승인; W1 100%는 [인수 매트릭스](docs/ACCEPTANCE_MATRIX.md) 충족 시에만 선언.
10. **갱신 시점·확인 범위·문서 커밋:** 2026-11-12 KST. 연결 GitHub의 최신 기존 소스/README/핵심 모듈과 해총 지침 확인, Factory 최초 문서 작성 범위. 최종 GitHub `main` HEAD 및 모든 feature refs는 초기화 종료 후 실제 검증 값을 보고하며 새 채팅은 재조회한다. **기능 미구현/QA 미검증/상업 출시 HOLD**.

## 다음 채팅 시작 문장
`너는 Factory AX 총괄이다. hibi89/factory-ax-ecosystem의 HANDOFF→STATUS→AGENTS→REQUIREMENTS→PRODUCT_BLUEPRINT와 최신 feature/data-verify 코드를 확인하고, 합성 제조업 4파일 실제 검수 엔진 구현부터 이어가라. ㄱ`
