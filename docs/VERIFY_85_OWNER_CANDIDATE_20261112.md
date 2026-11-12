> **2026-11-12 KST follow-up:** Native-readiness verification expanded without claiming 85%: 117/117 Linux Python PASS, Linux Xvfb real Tk smoke PASS, competing-backup unlink race fixed, Windows PowerShell owner script and manual-only dual-OS workflow expanded. **Windows native and GitHub Actions remain NOT RUN; W1 score remains 82%, 85 NOT ACCEPTED.** See [new evidence](VERIFY_82_QA_NATIVE_GATES_20261112.md).

# Factory AX VERIFY W1-85 target — offline owner candidate evidence

> 2026-11-12 KST. **Target 85%; verified engineering checkpoint currently 82% provisional, not the formal 85% gate.** Entire Factory AX Ecosystem is UNASSESSED. **RELEASE HOLD**, no real customer, no Production.

## Scope and design decision

Unchanged target: `docs/ACCEPTANCE_MATRIX.md` requires native Windows local GUI and package, bounded size/Korean output, basic security, failure/atomic new-only output, backup/recovery, zero-required API, clean CI, and static rights inventory. Two options: (A) PREP/EAI upstream multi-runtime bundled dependency (integration/redistribution rights not cleared; bigger installation complexity); (B) standalone local Python 3.11+ standard-library verify engine with explicit versioned mapping, bounded CSV/restricted XLSX, deterministic conservative rules, manual source SHA pinning, and a future adapter boundary. **B** selected for this isolated W1 checkpoint. Unmodified third-party/private product sources not copied; future parity/rights work remains.

## Implemented/checked at this exact staged source

- Old `factoryax.verify.main` API and 70% reconciliation retained; `python -m factoryax` now runs `factoryax.delivery.main` for owner-only report. Existing W1-50/70 tests still run.
- Four authorized role files re-read against per-file SHA and selected spec rechecked, before new report reservation. **This is sequential recheck and is NOT an atomic four-file snapshot**; malicious concurrent ancestors, Windows junction/ACL and approval provenance still need Windows-native exercise.
- New-only result directory via exclusive `mkdir`; three source-minimized internal JSON/public summary CSV/HTML generated in staging, hash receipt written last, `COMPLETE.sha256` committed last. Interrupted output must fail independent verifier; no overwrites, existing results preserved. Receipt **UNSIGNED, NOT an authenticity proof**. Existing legacy `verify.export_new` is available to older callers and has a weaker rename race; new packaged CLI/GUI uses delivery path.
- `factoryax.backup` manual new ZIP from validated owner output; restore exclusively into a new directory, validate SHA and reject unknown paths/unexpected members. No delete/replace/ERP/OT writes.
- Tkinter source GUI for selecting local approved spec/new report and reading review status; **headless import only, no displayed native Windows GUI validation**.
- Reproducible unsigned stdlib `.pyz` and `.cmd` launcher (requires separately installed Python 3.11+) plus self-contained SHA manifest, deterministic members and tamper check. `.pyz` executed as separate process on Linux synthetic 4-role data. This is not a signed EXE/Windows installer.
- Static `docs/DEPENDENCIES_AND_RIGHTS.md`; manual-only GitHub Actions workflow for Ubuntu/Windows prepared but **NOT EXECUTED** (private Actions minutes/billing authorization unconfirmed). No GitHub production service or external API.

## Actual tests and limitations

| Test / evidence | Result | Scope |
|---|---|---|
| `python -m unittest discover -s tests -q` | **115 PASS / 0 FAIL / 0 SKIP** | Linux Python3.13, synthetic only; includes preserved 87 old +28 new |
| `python -m compileall -q factoryax tests scripts examples` | **PASS** | Python syntax only |
| Deterministic build, independently unpacked `.pyz` CLI and receipt | **PASS** | Linux subprocess, not Windows |
| Backup/restore new-only, report/source/package tamper, traversal | **PASS** | Synthetic unit tests |
| GUI actual rendered Windows interaction / PowerShell / NTFS / Defender / SmartScreen | **NOT RUN** | No Windows in current runtime |
| GitHub-hosted clean Linux/Windows Actions on committed SHA | **NOT RUN** | Manual-only configuration, not proof |
| Customer CSV/XLSX/SMB/ERP BOM/ACL/large files/provenance/rights/pilot | **NOT RUN** | Synthetic demo only |

`python examples/make_reconcile_synthetic.py /absolute/new/demo`

`python -m factoryax --spec /absolute/new/demo/approved.json --output /absolute/new/demo/report-1`

`python -m factoryax --verify-report /absolute/new/demo/report-1`

`python -m factoryax --backup-report /absolute/new/demo/report-1 --output /absolute/new/demo/report-backup.zip`

`python -m factoryax --restore-backup /absolute/new/demo/report-backup.zip --output /absolute/new/demo/report-restored`

`python scripts/build_candidate.py --output /absolute/new/owner-package`

`python scripts/build_candidate.py --output /absolute/new/owner-package --verify`

`python /absolute/new/owner-package/FactoryAX-VERIFY.pyz --spec ... --output ...`

## Unresolved 85% acceptance blockers

1. **Native Windows QA**: real Windows 10/11 fresh Python, direct Tkinter GUI, `.cmd`/`.pyz`, Korean path, NTFS reparse/junction, concurrent output race and recovery, offline-mode network trace and buyer walkthrough not tested.
2. **Clean GitHub Windows/Linux CI** on committed SHA not run. Manual workflow must not be represented as completed test.
3. Full ACL/permission and multiple-file atomicity, authenticated owner approval, external customer license/rights, installed/offline packaging and actual customer support remain unproven. The chosen W1 stage requires a real Windows runtime before 85% accepted.

**Conclusion:** 70→**82% provisional engineering scope** (conservative +12 pp for owner candidate, receipt, backup/recovery, reproducible package and tests). **85% NOT ACHIEVED**; requires Windows/clean CI and acceptances, no subjective promotion. This checkpoint does not change overall Factory percent or the 16 active Kmong scores.

Rollback: previous feature HEAD `c324158c54753516aafba5f2aad85a09b277061a`; original `main@29b9653ccbc4bcd36a190f9e9d78954bcc4dae76` preserved. No force push/merge, no tokens/customer data, no external transmission. Release HOLD.
