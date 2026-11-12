# Factory W1 VERIFY — Windows one-click native acceptance candidate (2026-11-12 KST)

## Scope and decision
- Product: W1 VERIFY **82% provisional**, 85% native Windows/clean CI gate **NOT ACCEPTED**. Overall Factory AX Ecosystem UNASSESSED; RELEASE HOLD.
- User requested speed rather than more incremental patches. Reassessed two paths: (A) hosted GitHub Windows CI (workflow registered but **0 runs**, billing/dispatch inaccessible via connected tools), (B) a one-click synthetic Windows-native QA ZIP executable by the owner without GitHub Actions billing. Selected **B as independent unblock path**. A remains available through GitHub Actions.
- **Nothing in this document is a claim of native Windows PASS.** All current executed tests were on Linux.

## Executable candidate
- `RUN_FACTORYAX_WINDOWS_QA.cmd` (one click; normal user; no PowerShell policy bypass, no elevation).
- `scripts/owner_windows_qa.py`: verify read-only unsigned 21-file transfer manifest SHA256; Python version; full unit suite; four invented factory CSV; UTF-8 Korean input and report folders; reports and SHA256 receipts; backup/restore; repeatable zipapp; native `RUN_VERIFY_WINDOWS.cmd` return 0 and BLOCKED 3 with unchanged report; real native Tk widgets.
- `QA_SOURCE_MANIFEST.json` includes only source SHA-256s, not a signature, and cannot establish author identity. External shell/network/LLM not used. No customer data/real ERP/OT access.
- On native Windows the runner writes a **sanitized** JSON result in Windows temp. `RESULT_FILE:` is printed for owner review; do not automatically upload/share. Temporary synthetic input and reports are discarded. No user identifiers or raw records in summary.
- `README_WINDOWS_QA_KO.md` describes 3-step owner review. ZIP source has no embedded runtime or licensed binary/installer.

## Actually executed tests
- Linux Python3.13 individual files: test_verify 54, test_reconciliation 29, test_delivery 24, test_backup 15, test_profile_contract 4, test_malformed_rejection 4, new test_owner_windows_qa 4 = **134 PASS / 0 FAIL / 0 SKIP**. Files deliberately isolated due aggregate single-shot suite hitting execution timeout; no claim single-run all pass.
- Python compileall PASS. Clean ZIP extraction 21 source byte SHA256 PASS. `owner_windows_qa.py --plan` PASS; native runner called on Linux returned BLOCKED/exit3 (negative PASS).
- Windows CMD/GUI/NTFS/ACL/Defender **NOT RUN**; GitHub Actions total runs **0** at latest read. Product acceptance not upgraded.

## Remaining 85 gate
1. Authorized Windows10/11 ordinary non-OT PC: unzip source ZIP, double-click `RUN_FACTORYAX_WINDOWS_QA.cmd`, inspect local JSON result. If native tests pass, retain only sanitized JSON and manually review it before disclosure.
2. Or verify account included Actions minutes/spend caps, then manually dispatch existing Actions workflow on `feature/data-verify` (registered on main). Inspect Windows/Linux jobs, not merely `Ready`.
3. Evaluate Windows junction/ACL, real Excel export variety, installation/signing and support/right-to-distribute, no customer deployment until later 95/100 acceptance.

## Original/source safety
- No PREP/EAI/SMAX/HAE source copied or modified, no external API/real datasets, no main product merge, no paid hosted CI, no buyer. Git history allows revert without force.
- Record source HEAD remotely after write; workflow modifications affect only explicit manual dispatch, do not add auto triggers.
