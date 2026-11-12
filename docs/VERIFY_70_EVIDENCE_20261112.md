# Factory AX VERIFY W1-70 — synthetic engineering evidence (2026-11-12 KST)

## Product definition and exact milestone

- **First product only**: W1 CORE + VERIFY. This milestone covers conservative four-stage manufacturing reconciliation and owner policy drafting. The **whole Factory AX Ecosystem remains UNASSESSED**; W2–W4 not integrated, no sale/Production.
- Stage 70 from existing `docs/ACCEPTANCE_MATRIX.md`: linked purchase order → production (1:N NEW/REWORK) → quality inspection PASS/FAIL/REVIEW → shipments SHIP/RETURN, partial shipments, item+LOT grouping, explicit period and unit rules, source row evidence and supplier profile policy UI draft.
- **Two choices reviewed:** A) import PREP Node+EAI external engines (more multi-runtime/install/test/redistribution risk), B) self-contained Python3.11+ stdlib deterministic contract with explicit mapping and read-only SHA manifests (less dependency/cost and easier offline support, but parity with upstream remains unverified). **B chosen only for W1 local synthetic scope**; no proprietary PREP/EAI code copied. Original 50% engine preserved and extended additively. No external LLM/hosted service/subscription API calls.

## Execution / result

```
python -m unittest discover -s tests -q
python -m compileall -q factoryax tests examples
python examples/make_reconcile_synthetic.py /absolute/new/demo
python -m factoryax --spec /absolute/new/demo/approved.json --output /absolute/new/demo/new-review
```

- Source of truth is GitHub `feature/data-verify` commit (fill in after remote verification in reported handoff); local paths are temporary staging only.
- New synthetic business oracle covers D01 normal four roles, D02 1:N/multiple partial shipments, D03 lot/item/duplicate, D04 fail/return/rework/unauthorized movement, D05 precise decimal/unit/period/sequence, D06 malformed policy/mapping, D07 read-only, D08 SHA drift/no overwrite. No raw/customer data.
- Negative tests explicitly require REVIEW_REQUIRED or BLOCKED (not false OK). Group-level findings cite source-role+row without sensitive key strings. Reports are new-only HTML/CSV/JSON; original SHA preserved in CLI regression.
- Supplier `web/supplier_profile.html`: offline draft editor, no network fetch, no claimed approval. Draft `approved_by:null` is intentionally rejected by runtime until operator independently authorizes a real specification.
- Browser: Chromium synthetic inline `set_content` check (not direct `file://` URL verification); draft/flag/invalid date, console errors 0/network requests 0. Direct `file://` navigation blocked by browser policy (not proof of product failure).

## Invariants / gaps and next 85% conditions

- Input files must be under an approved absolute root, SHA-pinned; reject path escape, symlinks/known Windows reparse, invalid XLSX macros/formula and suspicious zip.
- Multiple sources scanned sequentially. Directory ancestor races and final cross-file atomic snapshot/re-stat are **NOT fully solved**; current per-file SHA is checked at read time, and all changes to authoritative customer sources must require a fresh independent review. Output no-overwrite is safer, but concurrent output name race is not formally proven on Win NTFS.
- Same-day events do not have time-of-day causal evidence; ambiguous relationships are deliberately held. `RETURN` offsets net only for explicit allowed case, no assumption that returned goods re-enter sellable inventory. `REWORK` is not counted as new production. Per-order per-LOT grouping is supported but not a full multi-line ERP accounting engine.
- No physical Win10/11, real Excel export diversity, multi-hundred-MB/large databases, real SMB, packaging/installer/uninstaller, cryptographic signer, verified role authorizations, real human approval UI, customer pilot, license/commercial acceptance. **RELEASE HOLD.**
- 85%: native Windows/packaged QA, clean CI, rollback/backup/ACL/race, full 10+ gold fixtures and factory staff UX, upstream PREP/EAI contract review and rights; 95% real isolated customer-shaped tests, 100% commercial signoff.
