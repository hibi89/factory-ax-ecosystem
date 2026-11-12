# Factory AX VERIFY W1 — isolated CI validation gate (2026-11-12 KST)

## Scope
- First product W1 CORE+VERIFY, 85% target, **82% provisional until actual Windows native validation**; whole Factory AX ecosystem UNASSESSED. RELEASE HOLD.
- Original source feature baseline `90d65dac113fbe553680a3b545f746b485ef8982`; no modifications to business/backup/GUI modules or customer sources.
- Problem: `python -m unittest discover -s tests -q` across the full suite sometimes exceeded runner/task wall-time; individual suites had already passed. Underlying resource/cross-test cause is not proven, so no unverified assertion that application runtime was hung.

## Tested workaround
- New `scripts/run_ci_regressions.py` discovers every `tests/test_*.py`, invokes Python unittest per test file with an isolated interpreter and bounded runtime, checks exit code + `Ran N tests`, refuses skips/zero/failed/timeout and emits JSON summary.
- Local isolated command: `python scripts/run_ci_regressions.py --timeout 50`.
- **Observed 2026-11-12 Linux Python3.13.5**: `{"status":"PASS","total_passed":134}`; 7 file suites with 15/24/4/4/4/29/54 PASS respectively, 0 failures/skips.
- Feature `.github/workflows/verify-owner-qa.yml` uses `--timeout 65` under the existing 12-minute job cap; preserves Linux Xvfb, Windows CMD blocked-exit and native Tk smoke steps. Workflow remains `workflow_dispatch` only with no push/PR auto triggers.
- Other existing local evidence: candidate owner ZIP with 21 SHA-pinned source members was verified against archive contents; **this does NOT prove Windows runtime behavior**.

## Unverified and required
- GitHub-hosted Actions run history **0** at inspection, account paid-billing balance/limits cannot be accessed; connected GitHub tools cannot dispatch.
- Actual Windows10/11 native QA/GUI, UTF-8 file paths, NTFS junction/race, Windows Powershell, AV/Defender, rights/legal inventory, installer and customer acceptance NOT RUN.
- **85% NOT ACCEPTED**, do not silently upgrade or declare production. Owner can select `feature/data-verify` from registered manual-only [Actions workflow](https://github.com/hibi89/factory-ax-ecosystem/actions/workflows/verify-owner-qa.yml) after confirming billing safety, or run the prepackaged local `RUN_FACTORYAX_WINDOWS_QA.cmd` and provide sanitized RESULT_FILE JSON.
