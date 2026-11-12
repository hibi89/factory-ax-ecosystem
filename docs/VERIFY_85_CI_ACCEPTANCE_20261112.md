# Factory AX VERIFY W1 — 85% engineering candidate CI acceptance evidence
> Confirmed 2026-11-12 KST. **Scope: W1 CORE+VERIFY only**. Entire Factory AX Ecosystem W2–W4 not implemented/scored. RELEASE HOLD.

## Verified exact revision and outcomes
- Private repo: `hibi89/factory-ax-ecosystem`, branch `feature/data-verify`, **tested source commit `b70a059175389bf53d87f8c90dc4f5bbe6a97986`**.
- [GitHub Actions #43178583600](https://github.com/hibi89/factory-ax-ecosystem/actions/runs/43178583600), completed **SUCCESS**, Ubuntu and Windows **both SUCCESS** on that exact SHA. This run supersedes the earlier red Windows runs; old failures are retained in history, not erased.
- Python 3.11 isolated regression **8/8 suites and 138/138 tests PASS / 0 FAIL / 0 SKIP on EACH runner**: backup17 + delivery24 + malformed4 + owner QA4 + profile4 + reconciliation29 + verify54 + Windows-flush-handle2. Python compileall PASS.
- Both runners passed deterministic unsigned local `.pyz`+Windows `.cmd` candidate build and SHA manifest verifier, synthetic four-role report generation/receipt verification, manual ZIP backup and restore verification.
- **Windows runner:** Hosted Windows Server 2025, Python 3.11.9. CMD report verification PASS; deliberate duplicate output `BLOCKED` exit **3** and existing result SHA unchanged PASS. Tkinter **actual widget invocation** PASS. Windows PowerShell 5.1 full synthetic script PASS, including Korean temporary paths, package manifest, backup/restore and GUI smoke. No source CSV/ERP write.
- **Linux runner:** hosted Ubuntu Python 3.11, real Xvfb Tk widgets synthetic PASS.
- Windows issue before this successful run: read-only handle `os.fsync` caused `OSError [Errno 9] Bad file descriptor`; limited cross-platform writable handle fix and regression tests were subsequently verified in this green CI. Other intermediate CI failures are historical, not current.
- No external AI service or network API is necessary for W1 execution. Inputs must be operator-authorized local synthetic/approved files with SHA mappings. SHA receipt is integrity only, NOT an authenticated human approval or signature.
- `docs/DEPENDENCIES_AND_RIGHTS.md` inventories original Factory-only Python stdlib code. **Runtime Python 3.11+ with Tk must be separately installed**. Candidate is unsigned `.pyz`/CMD, **not standalone signed EXE/installer**.

## Acceptance matrix interpretation
- **50%/70%:** four-stage Decimal/LOT/date/1:N/returns/rework conservative reconciliation, source row evidence, owner policy draft and negative oracle preserved by 138 regression tests.
- **85% — W1 engineering candidate ACCEPTED (provisional 85%, not commercial release):** isolated local Windows GUI/package candidate, Korean path, internal/external source-minimized HTML/CSV/JSON report, hash/size-bounded intake, deny/backup/new-only output, clean cross-OS CI, reproducible install-candidate SHA manifest, and static rights inventory established for synthetic tests.
- **Unverified/out of 85% synthetic evidence:** Windows 10/11 actual user machine, NTFS directory race/junction/ACL under adversarial workload, real Excel/MES exports and large-file performance, network-disconnected trace, signed installer/redistribution rights, genuine owner role-authentication, multi-file transactional snapshot, third-party golden parity, customer acceptance. These remain 95%/100% acceptance blockers (and any product requirement they affect must remain HOLD).
- **Whole ecosystem:** W2 knowledge/file/NAS, W3 HAE+LA security Guard, W4 endpoint/code QA/control console remain not integrated. No overall % assigned; product not commercially ready.
- GitHub Actions is metered on private repositories; one green Windows+Linux run is evidence, **not** an approval for unlimited paid CI. Current workflow uses bounded, branch-scoped source-triggered Linux and explicit `[windows-smoke]`/manual Windows matrix; budget settings remain owner-controlled.
- Future live installation/ERP/OT/customer/certification/production expressly excluded, RELEASE HOLD.

## Command reference
```sh
python scripts/run_ci_regressions.py --timeout 65
python scripts/build_candidate.py --output NEW_OWNER_PACKAGE
python scripts/build_candidate.py --output NEW_OWNER_PACKAGE --verify
python -m factoryax --spec APPROVED_LOCAL_SPEC --output BRAND_NEW_OUTPUT_DIR
python -m factoryax --verify-report NEW_OUTPUT_DIR
python -m factoryax --backup-report NEW_OUTPUT_DIR --output BRAND_NEW_BACKUP.zip
```
Windows source checkout on authorized ordinary PC, not OT:
```powershell
powershell.exe -NoProfile -File scripts/windows_native_qa.ps1 -GuiSmoke
```
Do not use real customer data for open CI. No customer consent or external upload is claimed. Roll back via Git history without force.
