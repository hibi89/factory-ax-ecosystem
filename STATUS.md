## 2026-11-12 KST — Registered Windows Tk synthetic QA in manual CI
- Main remains **registration/documents only**. Its manual-only `.github/workflows/verify-owner-qa.yml` is updated to include native Windows Tk widget smoke, still exclusively `workflow_dispatch`, guard `feature/data-verify`, contents read-only, 12-minute timeout and cancel-in-progress. **0 hosted Actions runs**, no automatic trigger or paid usage.
- Actual feature W1 VERIFY parent source `10b068b77cfc204c90de49b41736b851dc778c51` was extended with independent owner Windows one-click QA and 4 portable tests; feature commit `f3e2649c49a73c2621180bab115d30ef4a16ea1b`. Linux tests separated by file 134 PASS, full monolithic run timeout; clean ZIP hashes PASS. Actual Windows NOT RUN, VERIFY 82 provisional / 85 not accepted, ecosystem UNASSESSED, releases HOLD. No business code merged.

## 2026-11-12 KST — Manual-only CI registered on main; not run
- Owner explicitly authorized adding read-only, synthetic `workflow_dispatch` Windows/Linux CI registration at `.github/workflows/verify-owner-qa.yml` on default branch (registration commit `f54b74ebc5bd838c2305ae18672750fbad87ba4b`). Runs are guarded to `feature/data-verify`; actual hosted run count 0, account budget unverified. **Main still has no Factory product implementation**; development resides only on feature branch.
- Local staged feature regression 120/120 PASS and YAML structural checks PASS; native Windows/Windows CI unverified. W1 VERIFY 82% provisional, 85 not accepted; whole ecosystem UNASSESSED, RELEASE HOLD. No paid usage, customer data, automatic triggers, source merge, or permissions/billing changes.

# STATUS — Factory AX Ecosystem
> 2026-11-12 KST · **신규 Private 저장소 문서/브랜치 세팅 단계. 현재 개발은 아직 시작하지 않음.**

## 현재 사실
- GitHub `hibi89/factory-ax-ecosystem`: 사용자 생성, **Private**/default `main`; 새 저장소는 생성 시 빈 상태였고, 총괄이 초기 README/기준 문서/큰 기능군 브랜치 구성을 요청받았다.
- 확정 비전: 공장/보수적 기업 대상 **표준제품 납품형**, W1 CORE+VERIFY 진입→W2 KNOWLEDGE/FILE→W3 HAE+Lightning Azent·Security Guard·SOVIA/DBVORA→W4 PC CARE/Code QA/통합 Console.
- SMAX² 자체는 SELF 플랫폼으로 별도 유지. **PREP의 데이터 전처리 계약만** 기술 재사용 후보. REA_Web 전체 플랫폼은 W1 필수에서 제외.
- 신규 Factory AX 구현·운영 패키지·제조업 실자료·API·고객/실기기·CI/E2E·사업 거래 **0건**, 모든 제품 **RELEASE HOLD**. 완성률 **미측정**, 기존 원천 레포의 85%가 Factory 진척이 아님.
- 소유자·고객 계정/데이터, 권한/비밀/보안설정·클라우드·배포/지출·다른 GitHub 소스/브랜치 변경 **없음**.
- 문서 구성: `README.md`, `START_HERE.md`, `HANDOFF.md`, `STATUS.md`, `AGENTS.md`, `REQUIREMENTS.md`, `SCHEMA.md`, `docs/*`, `docs/workstreams/*`, `.gitignore`.

## 프로젝트/상용 진행 상태
| 목표 | 설계 | 기능 구현 | 테스트 | 출시 |
|---|---|---|---|---|
| W1 CORE+VERIFY | 작성 | NOT BUILT | NOT RUN | HOLD |
| W2 KNOWLEDGE/FILE | 작성 | NOT BUILT | NOT RUN | HOLD |
| W3 승인형 AX HAE/LA/SOVIA/Guard | 작성 | NOT INTEGRATED | NOT RUN | HOLD |
| W4 PC CARE/Code QA/Console | 작성 | NOT INTEGRATED | NOT RUN | HOLD |

## 첫 실제 작업(다음 `ㄱ`)
1. 신규 feature branch `feature/data-verify` 에서 PREP 계약과 EAI 현재 소스를 최신 SHA로 검수; **고객 자료 없는 제조업 4종 합성 스키마/독립 oracle**를 처음 만들고 테스트한다.
2. JavaScript PREP 직접 어댑터 vs Python port 두 안의 동등성·실행/유지보수 비용을 소스/벤치/사용권 기준으로 재검토, 승인된 목표 범위에서 하나 선택.
3. 최소 CORE/VERIFY 기능만 먼저. UI/보안/패키징은 병행할 수 있지만 실제 W1 E2E와 원본 불변·오류 보고 없이 상품 진행률 임의 상승 금지.
4. GitHub CI·Windows 실제 실행/고객 적합성·권리→`integration/develop` 통합→유료 고객 파일럿/출시 승인 전까지 HOLD.

## 문서/브랜치 검증
- 작성 작업 단위에서는 코드/실행/외부 서비스 변경이 없으므로 테스트 0/0이며, GitHub 파일/브랜치 HEAD는 작업 종료 시 **원격 재조회**해야 한다.
- GitHub 커밋 SHA는 self-referential 문서에서 추정하지 않는다. 종료 보고와 다음 채팅에서 실제 HEAD를 확인한다.
- Production URL/Vercel/Cloudflare 프로젝트: **미적용**, 별도 API/라이선스/환경변수 없음.
