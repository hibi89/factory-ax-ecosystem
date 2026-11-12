## 2026-11-12 KST — Owner Windows QA stability fix: per-file tests
- Clean QA ZIP candidate runner moved from monolithic `unittest discover` (exceeded local process wall-time) to seven independently bounded per-file regressions. Local `test_owner_windows_qa.py` 4 PASS, new independent ZIP extraction 21/21 SHA256 PASS, --plan now lists 7 per-file tests and Linux non-native invocation correctly BLOCKED exit3. Source SHA `62671c332ca7be3cef93f6f82d538f48c055123a`, manifest SHA `c1db5ef2c7a6b61bb133ad98c0188ec0ae4b8b47`, exact tested local bytes. Previously independently tested full 134 Python tests (7 files) PASS. No native Windows CI/test executed; 82% provisional, 85 NOT VERIFIED, Factory entire ecosystem UNASSESSED, RELEASE HOLD.

## 2026-11-12 KST — One-click Windows native QA candidate, VERIFY 82% provisional
- User requested accelerated 85 gate resolution. Source-controlled one-click normal-user Windows QA: `RUN_FACTORYAX_WINDOWS_QA.cmd`, `scripts/owner_windows_qa.py`, `QA_SOURCE_MANIFEST.json`, `README_WINDOWS_QA_KO.md`, `tests/test_owner_windows_qa.py`, `docs/VERIFY_82_WINDOWS_ONECLICK_QA_20261112.md`; manual-only workflow Windows now explicitly runs real Tk synthetic GUI smoke. **No auto-run or paid Actions triggered.**
- Linux Python3.13 tests file-by-file: verify54 + reconciliation29 + delivery24 + backup15 + profile4 + malformed4 + new Windows entrypoint4 = **134 PASS, 0 FAIL, 0 SKIP**. Monolithic run exceeded environment timeout; file-split complete. compileall PASS. Clean ZIP extract verified 21 source SHA-256 and --plan PASS; native runner on Linux correctly BLOCKED exit3.
- ZIP `FactoryAX_VERIFY_WINDOWS_ONECLICK_QA_20261112.zip` delivered in conversation; unsigned/source-only, Python >=3.11 required. Windows owner can download/unzip and double click. The test runs only invented data in temporary workspace, sanitizes JSON result, no external API, admin rights or security-policy bypass.
- Actual Windows native CMD, Tk, NTFS/ACL, licensing/security/Defender and hosted Actions CI **NOT RUN** (0 workflows). VERIFY **82% provisional**, 85 acceptance NOT MET; Factory whole ecosystem UNASSESSED, RELEASE HOLD. Python source and real OS evidence are separate.
- Preserve original main business code, PREP/EAI/HAE/SMAX repos, no transfer of private/customer files. New source/manifests backed up via branch history; verify HEAD after commit. Next best step: run single owner Windows QA or explicitly dispatch existing synthetic-only feature workflow after quota review; inspect JSON/CI logs, then reassess 85.

## 2026-11-12 KST — Path ancestor read/write safety hardening, VERIFY W1 82% retained
- Verified baseline `7ac39e8009e3c2312e1f2b616ec66f0d1d237794`. Added component-wise `lstat` all-ancestor directory guard against POSIX symlink/Windows reparse alias for spec, approved root, report, backup and restore. This is conservative preflight, NOT atomic Windows handle+ACL protection. No PREP/EAI/etc source copied/changed.
- Linux Python3.13 **130 PASS/0 FAIL/0 SKIP**, counted from six individually completed module suites (15+24+4+4+29+54); two separate monolithic full-suite invocations reached process time limits without completion and are **not** claimed PASS. `compileall` PASS; clean unsigned ZIPAPP build+verify, synthetic 4-stage CLI/report+backup+restore integrity and real Tk/Xvfb GUI PASS.
- Exact new feature code/test blobs must match local SHA: delivery `67855be8149ed2caa137a852f73947218903da07`, backup `49d4a55b4e2fd8660f18e412896dd7f0829580f2`, delivery tests `707bc70eba1faa3450a2fc77a32e7cb036441544`, backup tests `980cfac2cafd304967ad2ca4222f23fc491ec5a6`. Full evidence: `docs/VERIFY_82_PATH_ANCESTOR_QA_20261112.md`.
- GitHub Actions 0 runs seen; native Windows CMD/PowerShell/Tkinter/NTFS/ACL/junction, account compute budget, real customer and commercial rights NOT VERIFIED. W1 VERIFY **82% provisional engineering**, **85% NOT ACCEPTED**; full Factory Ecosystem UNASSESSED. RELEASE HOLD. No main changes, paid CI, customer uploads or deployment.
- Next external hinge: owner checks Actions usage/budget and manually launches `feature/data-verify` QA; exact hosted Windows/Linux logs and owner native Windows test needed for 85 reevaluation.


## 2026-11-12 KST — W1 VERIFY malformed JSON fail-closed hardening (82% maintained)
- Real input-contract issue: approved spec [] and malformed report/receipt/backup JSON shape could cause unhandled Python exceptions instead of BLOCKED. Added structural checks and four CLI negative tests expecting exit3, no traceback and no unwanted output.
- Linux Python3.13.5 targeted 4 PASS; complete verbose suite 124 PASS/0 FAIL/0 SKIP (34.928s); compileall PASS; .pyz package build and integrity verifier PASS. Initial combined runner wrapper timed out; separate verbose diagnostic run completed OK.
- Default-branch manual CI previously registered with approval; GitHub Actions 0 hosted runs; account billing/Windows native not inspected. No paid CI execution or product main changes.
- VERIFY W1 82% provisional, 85% NOT accepted; whole Factory ecosystem UNASSESSED, all releases HOLD. Baseline feature SHA 001e9f2f5c3c14a4904cfda90c64aa8835a13d6c, latest SHA from GitHub ref after commit. Evidence docs/VERIFY_82_MALFORMED_FAILCLOSED_20261112.md.

## 2026-11-12 KST — Owner-approved manual QA registration, hosted CI NOT RUN
- Explicit approval received to register the manual-only QA workflow on default `main`. Workflows on `main` and `feature/data-verify` now use `workflow_dispatch` exclusively, read-only `contents` permission, a `feature/data-verify` job guard, 12-minute per-job timeout, and cancel-in-progress concurrency. Workflow is synthetic-only; no production or customer data.
- `main` workflow registration SHA **f54b74ebc5bd838c2305ae18672750fbad87ba4b**; feature workflow update SHA **f6915c12aba6b02280029d74eac8e5778844d560**. The existing functional feature code SHA **0c3f1cb9d610ae90a7d1f132a985e7636becfca1** and the default baseline functional documents were not merged/replaced.
- Local Python3.13.5 exact staged sources: `python -m unittest discover -s tests -q` **120 PASS/0 FAIL/0 SKIP**, compileall PASS. PyYAML structural dispatch/branch/timecap/concurrency check PASS. Actual runner CI remains **0 workflow runs**; no native Windows/PowerShell, owner account Actions usage/budget, signed installer, NTFS or real customers verified.
- **VERIFY W1 stays 82% provisional; 85% NOT ACCEPTED.** Whole Factory ecosystem UNASSESSED. All RELEASE HOLD. The approved GitHub change does not authorize paid compute, billing/security-settings changes or customer data processing.
- Next: owner checks `https://github.com/settings/billing` usage and budgets (including "Stop usage when budget limit is reached"); only then deliberately dispatch the manual run selecting `feature/data-verify`. Connected GitHub tools can inspect runs but **cannot dispatch** them. Review Windows/Linux job logs and owner PC acceptance before any score upgrade.

## 2026-11-12 KST — VERIFY backup source capture race mitigation (82% pending)
- Starting audited SHA `f687b4affb0f973534734965d98d3d3b70dfd91c`. Fixed a real backup validity gap: a source report could mutate between `verify_candidate` and separate backup file reads, yet backup could report success. Backup now independently rechecks captured bytes against receipt, completion SHA and report manifest/status, then validates source again after writing ZIP; failure removes only its own partial archive. This is NOT a transactional cross-file snapshot or a signed identity protocol.
- Linux Python3.13.5: `python -m unittest discover -s tests -q` **120 PASS/0 FAIL/0 SKIP**, 2 added concurrent source mutation regressions; `python -m compileall -q factoryax tests scripts examples` PASS; offline reproducible .pyz build+manifest validation PASS; Linux Xvfb real Tk synthetic 2-button flow PASS.
- GitHub Actions hosted runs **0**; native Windows NTFS/ACL/Defender/CMD and customer environment **NOT VERIFIED**. The `workflow_dispatch` exists only on feature ref, not main; private Actions billing allowance/owner approval unknown. No automatic paid run or default-branch changes.
- **W1 VERIFY stays 82% provisional engineering / 85 NOT ACCEPTED**; Factory AX Ecosystem UNASSESSED, W2–W4 NOT BUILT, RELEASE HOLD. Feature only. [Evidence](docs/VERIFY_82_BACKUP_CAPTURE_QA_20261112.md).
- Next gated step: obtain owner consent for default-branch manual CI registration and billing confirmation, then Windows CI and approved physical PC test; if unavailable maintain unverified. Source old SHA is rollback; new SHA fetch from GitHub.

## 2026-11-12 KST — Windows CMD fail-closed launcher fix; W1 VERIFY remains 82% / 85% NOT ACCEPTED
- Confirmed exact starting feature SHA `84ed826aeba5a9b438e91d865a546e67fb7014df`; reviewed private Actions run history (0 runs) and GitHub official runner billing/dispatch requirements. Private Windows runner draws from monthly included compute allowance before possible charges; remaining account allowance and paid cap are NOT available, so **no hosted CI started**.
- Fixed concrete generated Windows CMD errorlevel bug: `if %errorlevel% equ 0 (... exit /b %errorlevel%)` expands the variable before inner command execution and could conceal BLOCKED exit=3. New `goto use_python` branches execute ZIPAPP and `exit /b %errorlevel%` on separate command lines. Added static regression and native Windows CI/owner PowerShell negative tests requiring exit3 and unchanged prior output.
- Executed Linux Python3.13.5 `python -m unittest discover -s tests -q`: **118 PASS/0 FAIL/0 SKIP**; `compileall`, deterministic Python .pyz bundle build/verification, Linux Xvfb real GUI owner synthetic smoke PASS. No native Windows interpreter, cmd.exe, NTFS, SmartScreen, Windows PowerShell or Windows Actions run available.
- Windows workflow is `workflow_dispatch` only and lives on feature branch, not default `main`. GitHub documentation requires the file on default branch for a manual Run workflow button. Do not merge/alter main, enable paid usage, change security policies or create auto-triggering jobs without owner's explicit approval.
- **Scoring:** W1 VERIFY **82% provisional engineering**, 85 native gate **NOT PASSED**. Whole Factory Ecosystem UNASSESSED. RELEASE HOLD. Exact revised feature SHA must be fetched remotely; no inherited PREP/EAI completeness, no customer data or actual sale. See `docs/VERIFY_82_WINDOWS_LAUNCHER_QA_20261112.md`.
- Next: verify billing budget and approval; register manual-only dispatch workflow on default with explicit consent, trigger `feature/data-verify` only and inspect clean Windows/Linux logs; then native owner PC GUI/ACL/Korean/NTFS/Defender acceptance. No silent 85 claim.

## 2026-11-12 KST — W1 VERIFY 85 target: safety/GUI QA extension, score 82% provisional unchanged
- Exact code source GitHub commit `eca3222e5588aac41c3fbf700192cd4d707d1323`, remote 9 changed Git blobs verified against local `git hash-object` values. Original `main` and 70% engine unchanged; no commercial release.
- Fixed backup competing-writer race: `open('xb')` FileExistsError no longer unlinks another process's archive, and failed write only cleans same device/inode. Two new negative tests. Fixed Tk owner UI cancellation default path and stale success text.
- Local Linux3.13.5 `python -m unittest discover -s tests -q` **117 PASS/0 FAIL/0 SKIP**, `compileall` PASS. Actual Tk Xvfb GUI flow two invocations + canceled chooser PASS, source bytes unchanged. Four-role invented CLI report→verify→backup→restore→verify, reproducible unsigned .pyz build/verifier PASS. Synthetic only.
- Native Windows QA script `scripts/windows_native_qa.ps1` added; manual-only `.github/workflows/verify-owner-qa.yml` expanded for Linux/Windows synthetic and Linux Xvfb. **GitHub Actions runs=0, Windows native/PS5.1/NTFS/Defender/real desktop NOT RUN** (private minutes approval unknown). Do not claim 85%.
- **W1 VERIFY remains 82% provisional engineering, target85 BLOCKED BY native Windows/clean CI and true authorization/snapshot acceptance; entire Factory Ecosystem UNASSESSED, W2–W4 not integrated, all RELEASE HOLD**. See `docs/VERIFY_82_QA_NATIVE_GATES_20261112.md`. No customer/OT data, API, paid CI, production or entitlement change.

## 2026-11-12 KST — VERIFY W1-85 candidate developed, 82% provisional; 85 NOT ACCEPTED
- Existing W1-70 conservative 4-role reconciliation unchanged; added new-only owner report protocol, post-analysis per-source SHA recheck, independent 3-report SHA receipt + completion sentinel, explicit report verification, manual ZIP backup and restore, local Tkinter GUI source, deterministic unsigned Python .pyz plus Windows .cmd launcher, manifest verifier. No upstream PREP/EAI copying.
- At exact staged source, Linux Python3.13 full **115 PASS / 0 FAIL / 0 SKIP**, compileall PASS, clean isolated .pyz CLI synthetic run PASS, deterministic package and restoration/integrity/tamper tests PASS. No real Windows GUI/display or NTFS/ACL, clean GitHub Actions at new SHA, actual Win10/11/installer/defender/customer/rights. workflow_dispatch-only CI file prepared, NOT RUN due private minutes/billing uncertainty. 
- **W1 VERIFY 82% provisional engineering** (70%+12%p scoped), **85% not achieved** because Windows/CI native gate remains. Whole Factory AX Ecosystem UNASSESSED. Every module RELEASE HOLD. No production, no signed EXE, no customers or secret data. Existing legacy export_new is less race-safe; packaged user path uses new delivery protocol, still not atomic four-source snapshot.
- Feature baseline HEAD `c324158c54753516aafba5f2aad85a09b277061a`, original main untouched. Sources: `factoryax/delivery.py`, `backup.py`, `gui.py`, `scripts/build_candidate.py`; tests `tests/test_delivery.py`, `tests/test_backup.py`; evidence `docs/VERIFY_85_OWNER_CANDIDATE_20261112.md`; source rights inventory `docs/DEPENDENCIES_AND_RIGHTS.md`. Checkout feature exact HEAD to check and rerun. Windows CI, buyer approval and real native packaging are next formal 85 gates.

## 2026-11-12 KST — VERIFY W1-70 provisional scope, 87 local PASS
- Factory first product **VERIFY 70% provisional engineering** (NOT entire Factory ecosystem; W2–W4 UNASSESSED/NOT BUILT). Four-stage purchase order→production→quality→shipment exact LOT/item joins, decimal sums, 1:N/partial, return/rework policy, event-date ordering/cumulative availability, missing/duplicate evidence, conservative REVIEW, no source writes. Versioned explicit policy and offline supplier draft UI (not authenticated approval).
- Baseline W1-50 preserved. Python3.13.5 Linux source/test `python -m unittest discover -s tests -q` **87 PASS / 0 FAIL / 0 SKIP**, compileall PASS; invented 4-source end-to-end CLI **OK/0**, reports JSON/HTML/CSV, source hashes unchanged. Negative policy/lot/return/early-shipment tests return REVIEW/BLOCKED. Chromium same-source `set_content` 3/3 UI scenarios, 0 page errors, 0 outbound requests. Direct `file://` load was **BLOCKED BY BROWSER POLICY**, thus real direct Windows file:// NOT VERIFIED.
- GitHub exact source blobs: verify `d223747b600958c142f80ac7563c0fb2c4dcbf4a`, reconcile `50087c130b96a6f47451c5dd062dd027d9a7cc60`, new oracle tests `734e4e1932a2ea67f21e88b38e2a97c238c06765`; refs/branch SHA after commit to be read anew. Legacy `main@29b9653c...` preserved. `docs/VERIFY_70_EVIDENCE_20261112.md`.
- **Unverified:** no native Windows, full BOM/ERP semantics, single atomic cross-file snapshot, customer licensing/authority or upstream PREP/EAI golden contract parity, GitHub Actions clean CI, installer, API, production. Local synthetic test != release. All **RELEASE HOLD**. Next W1 85%: clean CI/Windows package, independent rights, signed/real owner approval/ACL/race cases, customer-shaped E2E. Rollback: feature branch Git history, no force/merge or external source changes.

## 2026-11-12 KST — Factory VERIFY first executable W1-50 checkpoint (feature only)
- Product: **Factory AX VERIFY W1 50% provisional engineering milestone**, limited basic intake/quality. **Whole Factory AX Ecosystem completion remains UNASSESSED**, W2-W4 NOT BUILT, all **RELEASE HOLD**. No customer release claim.
- Original Python 3.11+ stdlib local offline code: four manually approved synthetic/authorized CSV/restricted XLSX sources; exact source SHA, row provenance, versioned mapping; five quality rule families, OK/REVIEW_REQUIRED/BLOCKED; new-only HTML/JSON/CSV summary.
- Local synthetic same source/test files: **54 PASS / 0 FAIL / 0 SKIP**, compileall PASS; actual synthetic four-file CLI return OK; negative CLI review/blocked and no overwrite tested. Product blob SHA `dc4be03b682679211d16aed7c3efd6ac45c41f82`; tests blob SHA `30e014751b2e8c7511d4493d3fde31749ed51d94`; example blob `f7b26da338948e9d4dc404c52cf220f1dc1fdee3`. Exact GitHub blobs verified against local bytes.
- **NOT VERIFIED**: PREP source golden parity (new standalone PREP has no GitHub runtime), EAI integration, cross-stage 1:N and returns/date/quantities, Windows 10/11 PC and Excel exports, concurrency race-free persistence, customer rights/security, installer/CI/Production. Only limited quality OK, not product/customer acceptance.
- Repo `hibi89/factory-ax-ecosystem@feature/data-verify`; baseline `main@29b9653ccbc4bcd36a190f9e9d78954bcc4dae76` untouched. Run `python -m unittest discover -s tests -q` and `python examples/make_synthetic.py /absolute/new/demo`. Evidence `docs/VERIFY_50_EVIDENCE_20261112.md`, user can recover baseline without force.


---

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
