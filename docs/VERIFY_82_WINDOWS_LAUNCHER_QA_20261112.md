# Factory AX VERIFY W1-85 Windows launcher follow-up — 2026-11-12 KST

## Verified and scope
- First product W1 VERIFY currently **82% provisional engineering**; **85% not accepted**, entire Factory AX Ecosystem **UNASSESSED**, sale/production RELEASE HOLD.
- Source branch: private `hibi89/factory-ax-ecosystem@feature/data-verify`. Baseline before this fix: `84ed826aeba5a9b438e91d865a546e67fb7014df`; all source roots/feature main and other product repositories preserved.
- Found real **batch programming defect** by code analysis: `if %errorlevel% equ 0 ( py ... & exit /b %errorlevel% )` uses CMD parse-time expansion for `%errorlevel%`. A returned BLOCKED(3) could be falsely reported as success(0). Updated Windows CMD launcher to branch via `goto use_python` and run `exit /b %errorlevel%` on a distinct line, with launch under installed `py -3` or fallback `python`.
- Added `test_windows_launcher_preserves_blocked_exit_code` static regression, Windows GitHub Actions `pwsh` step to execute generated CMD and confirm negative exit3 and unchanged report SHA, and same test in `scripts/windows_native_qa.ps1`. Actual Windows runtime behavior is **not** established by Linux static tests.

## Execution
| Check | Result | Meaning |
|---|---|---|
| Linux Python3.13.5 full unittest | **118/118 PASS, 0 FAIL, 0 SKIP** | Existing 117 maintained, plus 1 CMD static regression |
| Linux `python -m compileall -q factoryax tests scripts examples` | PASS | Syntax only |
| Deterministic `.pyz` build + verify manifest | PASS | Local offline package, no installer/signature |
| `xvfb-run -a python scripts/gui_smoke.py` | PASS | Real GUI widget invocation under Linux Xvfb, NOT native Windows |
| Windows `RUN_VERIFY_WINDOWS.cmd` blocked error propagation | **NOT RUN** | Native Windows CI step prepared |
| GitHub Actions hosted Windows/Linux CI | **NOT RUN (0 runs seen)** | Workflow dispatch requires default branch registration + account usage approval |
| Real Windows10/11 NTFS junction/ACL/Korean/signed installer/Defender | NOT RUN | Native/customer acceptance unverified |
| Customer/licensing/retail release | HOLD | Not authorized or accepted |

## GitHub Actions pricing and release gates
- GitHub's current official documentation states GitHub Free private-repo monthly included compute usage may be **$12**; standard Windows two-core runner rate **$0.010/min**; included usage is shared with eligible compute and may be exhausted. **Account balance/remaining monthly usage and spending controls not accessible to this workflow.** Never promise zero charge based only on public quota. See https://docs.github.com/en/billing/reference/product-usage-included and https://docs.github.com/en/billing/reference/actions-runner-pricing
- Official GitHub documentation: manual `workflow_dispatch` executes only when the workflow file exists on the **default branch**. Our QA workflow exists only on `feature/data-verify`; current `main` does not register it. See https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
- Option A: after explicit owner permission, register a manual-only QA dispatcher on default `main`, preserving existing stable functional code; then select `feature/data-verify` and run Windows/Linux matrix after checking remaining usage/cap. Requires main change and possible metered GitHub Actions use.
- Option B: owner runs `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows_native_qa.ps1 -GuiSmoke` on approved local ordinary Windows PC, from a trusted source checkout. No hosted runner metering, but native safety/Defender/SmartScreen and shell command evidence must be reviewed; no security bypass required.
- **Recommendation:** maintain current branch and score without charges or forced main changes, request clear approval for A or use B. If none possible, **85 remains UNVERIFIED**.

## Recovery and non-goals
- Existing candidate/report output uses exclusive new-only creation, unsigned source receipts, read-only input SHA validation; no customer files exposed. New negative CMD test explicitly denies overwriting earlier report.
- This fix does not provide standalone signed Windows .exe, installed Python runtime, transactional snapshot over four simultaneous source updates, true owner authentication or production compliance.
- Rollback: Git history prior SHA `84ed826aeba5a9b438e91d865a546e67fb7014df`, no force push, no main branch changes.
