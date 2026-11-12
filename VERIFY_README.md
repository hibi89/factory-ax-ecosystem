> **CURRENT 2026-11-12 W1 CHECKPOINT:** [Verified hosted Linux+Windows CI #43178583600](https://github.com/hibi89/factory-ax-ecosystem/actions/runs/43178583600) exact feature SHA `b70a059175389bf53d87f8c90dc4f5bbe6a97986`: **138/138 PASS on each OS**, build/manifest/report/backup/restore, Windows Tk widgets, CMD BLOCKED exit3, PowerShell5.1 Korean paths PASS. **W1 VERIFY 85% provisional engineering candidate accepted**; package is unsigned .pyz requiring separately installed Python3.11+Tk; no customer Windows10/11/real ERP/installer or commercial permission. **Factory AX total UNASSESSED; RELEASE HOLD**. [Evidence](docs/VERIFY_85_CI_ACCEPTANCE_20261112.md). Below are historical earlier-stage notes.


---

> **2026-11-12 current checkpoint:** W1 VERIFY **82% provisional (85 target NOT verified)**, entire Factory ecosystem UNASSESSED. Linux 117/117 synthetic unit PASS, real Linux Tk/Xvfb QA PASS, local .pyz/backup PASS; native Windows, clean Actions and customer approval NOT RUN. See [native-readiness evidence](docs/VERIFY_82_QA_NATIVE_GATES_20261112.md). All sale/release HOLD.

# Factory AX VERIFY — restricted local W1 prototype

This is a 50%-stage *prototype* for the first Factory AX VERIFY product, **not** a 50% complete Factory AX Ecosystem. No customer deployment. `RELEASE HOLD`.

## Requirements

Python 3.11+; only standard library. No server, telemetry, or external AI calls. All files must have approved mappings and an exact SHA256. A local customer must approve each manifest separately; `human_approved:true` in JSON is not an authenticated approval or a security signature.

```sh
python examples/make_synthetic.py /absolute/new/synthetic-demo
python -m factoryax --spec /absolute/new/synthetic-demo/approved.json --output /absolute/new/synthetic-demo/review-1
python -m unittest discover -s tests -q
```

Exit 0 = `OK` only for limited input-quality rules; exit 2 = `REVIEW_REQUIRED`; exit 3 = `BLOCKED` (no output). Existing output paths are rejected. Supported CSV UTF-8 BOM or no BOM and formula-free restricted XLSX with one visible sheet. The role-specific mapping requires `record_id`, `order_id`, `item_id`, `lot_id`, `quantity`, `unit`, and `inspection_status` on quality files. `approved_units` requires explicit symbols such as `EA`. No auto-conversion. Source files are never modified.

Synthetic examples can be shared; **do not commit real customer files, credentials or internal folders**. Original PREP/EAI files are not bundled. Documented source/permission/RACE/XLSX limitations and next-stage requirements: `docs/VERIFY_50_EVIDENCE_20261112.md`.

## W1 70%-stage conservative four-stage reconciliation (provisional)

This stage is **not** a 70% complete Factory AX Ecosystem, industrial quality certification, or commercial release.

```sh
python examples/make_reconcile_synthetic.py /absolute/new/factory-demo
python -m factoryax --spec /absolute/new/factory-demo/approved.json --output /absolute/new/factory-demo/review-new
python -m unittest discover -s tests -q
```

The v0 optional `reconciliation_policy` makes four-stage reconciliation mandatory; without it, the CLI still provides its previous W1-50 quality-only checks (the unchanged legacy behavior is not W1-70 completion). The 70-stage policy requires explicit `approved_by`, date boundaries, bool rules, a capped Decimal tolerance, and `event_date` on every role plus `movement_kind` for production/shipment. It is a self-declared business-rule acknowledgement, **not** an authenticated approval or digital signature. No automatic unit conversion. Only supported `NEW/REWORK`, `SHIP/RETURN` and `PASS/FAIL/REVIEW` are accepted. Unclear ordering, later inspections, invalid/early returns, missing lots, and overages are held for review. Quantity totals use Decimal (no float), source row citations exclude raw field values.

Supplier policy draft UI is the standalone local `web/supplier_profile.html` (no upload/server/CDN; it only displays a draft JSON with `approved_by:null`). The actual approved mapping, SHA receipts, and input files are separate, locally controlled by the operator; drafts cannot be executed as approved policies.

**Limits:** current policy does not model BOM, exchanges, multi-plant/warehouse, all ERP date conventions, per-piece quality disposition, returned inventory resale, time-of-day same-day sequencing, role/actor authentication, or physical Win/SMB security. No real customers or external secrets were used. Full test/QA evidence: `docs/VERIFY_70_EVIDENCE_20261112.md`. `RELEASE HOLD`.

## W1 85 target — owner-only delivery candidate (currently 82% provisional, **85 NOT VERIFIED**)

The `python -m factoryax` entrypoint now uses the hardened owner-only delivery path. Old `factoryax.verify.main` remains callable for legacy regression, but its direct output function does not provide the new completion/backup protocol. The standard package uses Python 3.11+ **not bundled** and requires no paid API or server.

```sh
python examples/make_reconcile_synthetic.py /absolute/new/demo
python -m factoryax --spec /absolute/new/demo/approved.json --output /absolute/new/demo/report-1
python -m factoryax --verify-report /absolute/new/demo/report-1
python -m factoryax --backup-report /absolute/new/demo/report-1 --output /absolute/new/demo/backup.zip
python -m factoryax --restore-backup /absolute/new/demo/backup.zip --output /absolute/new/demo/restored
python scripts/build_candidate.py --output /absolute/new/owner-bundle
python scripts/build_candidate.py --output /absolute/new/owner-bundle --verify
python /absolute/new/owner-bundle/FactoryAX-VERIFY.pyz --spec /absolute/new/demo/approved.json --output /absolute/new/demo/report-2
python -m factoryax --gui
```

A `COMPLETE.sha256` receipt and report metadata are **unsigned** and do not authenticate the owner. Interrupted/corrupted report directories are not reusable. Restore never overwrites. Input file rechecks are sequential and **not a four-file transaction**. The Tkinter GUI is source-implemented but native Windows physical UI still NOT RUN. Internal `RUN_VERIFY_WINDOWS.cmd` is QA-only, not signed or installed. Existing source records remain read-only. Every result/backup is local and caller-selected. See [85 target evidence](docs/VERIFY_85_OWNER_CANDIDATE_20261112.md) and [rights inventory](docs/DEPENDENCIES_AND_RIGHTS.md); release HOLD.

## W1 85 native QA preparations (NOT a Windows PASS)

Run locally on an **authorized non-OT Windows 10/11 PC**, from the checked-out source and after reviewing `scripts/windows_native_qa.ps1`:

```powershell
powershell.exe -NoProfile -File scripts/windows_native_qa.ps1
# Optional displayed Tkinter synthetic QA if the Windows desktop is available
powershell.exe -NoProfile -File scripts/windows_native_qa.ps1 -GuiSmoke
```

On Linux with a graphical test display: `xvfb-run -a python scripts/gui_smoke.py`.
The GitHub Ubuntu+Windows test matrix is **manual-only**; run only after authorizing private GitHub Actions usage/minutes. Do not imply success from preparing these scripts.
