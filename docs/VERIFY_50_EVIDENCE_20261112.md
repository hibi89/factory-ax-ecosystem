# Factory AX VERIFY — W1 50% first executable checkpoint

- Date: 2026-11-12 KST, **synthetic-only**; original blueprint `docs/ACCEPTANCE_MATRIX.md` unchanged.
- Definition: 50% is **first W1 VERIFY acceptance-gate milestone**, not Factory AX Ecosystem total completion. RELEASE HOLD.
- Ownership: independently authored Python3.11+ stdlib prototype; original PREP/EAI repos/branches untouched and no copied proprietary source. Contract interoperability is conceptual only; **actual upstream golden parity not run**.

## Independent implementation evidence

1. Local explicit approved four-file `purchase_order`, `production`, `quality_inspection`, `shipment` profile; exact expected SHA-256 per source; data remains on client disk.
2. UTF-8(-BOM) CSV and restricted single-visible-sheet formula-free XLSX intake with bounds, path/symlink guards, extension/magic checks, duplicate/missing headers, manual field maps and versioned schema.
3. Provenance `source_id` + real 1-based row, source SHA/size/source_rows, explicit company profile/rule versions; no raw business identifiers in exported report. Three result states: `OK` (basic input quality scope only), `REVIEW_REQUIRED` (quality issue), `BLOCKED` (unsafe/ambiguous input).
4. Quality rule families: required fields, record-ID duplicates, finite positive Decimal/approved units, order/item/LOT reference orphan, inspection not PASS/unknown. Cross-stage quantity reconciliation, returns/rework/date, parent quantities and unit conversions explicitly **not yet implemented** (70% stage).
5. New-directory only output `result.json`, `summary.csv`, `summary.html` (no JS, CSP, no raw values), synthetic CLI successful and review/blocked exit codes 0/2/3.

## Test and execution scope

```bash
python -m compileall -q factoryax tests examples
python -m unittest discover -s tests -q
python examples/make_synthetic.py /tmp/factoryax-new-demo
python -m factoryax --spec /tmp/factoryax-new-demo/approved.json --output /tmp/factoryax-new-demo/review-1
```

- Initial Linux/Python3.11-equivalent container run: **54 tests PASS / 0 FAIL / 0 SKIP** (27 cases duplicated through inherited audit suite); compileall PASS; four CSV, four XLSX, mixed types, output, SHA invariants, malformed Excel/CSV, denial paths tested.
- Did not run GitHub Actions, physical Windows 10/11, Excel/Office actual exports, PREP golden parity, EAI native integration, customer data, installers, networking/firewall captures, malicious ZIP corpus, actual supplier mapping, perf/limits.
- Non-atomic multi-file capture / directory reparse race / directory-rename race at concurrent writers remain known gaps. `OK` means only supported basic rules, **not quality approval**.

## Design decision A/B

| Strategy | Speed | Ongoing cost and security | Decision |
|---|---|---|---|
| A. Copy PREP Node/EAI internals and install 2 runtimes | quick if rights/compatibility cleared | dependency/security complexity, rights parity incomplete | NOT chosen |
| B. Original Python stdlib gated micro-core + versioned adapter/parity later | moderate first build | no paid API, one runtime, independent rights and deterministic QA | **Chosen for synthetic W1 checkpoint** |

## Later gates

**70%:** full manufacturing 1:N partial shipment/rework/returns, negative/unit/date policy, mapping UI, 10 oracle scenarios, source drift across all four files. **85%:** native Windows GUI, packaging, security review, verified backup/restore. **95%:** physical Windows/isolated network/customer-shaped tests. **100%:** actual rights/price/support/customer signed acceptance and owner release approval.

STOP if source rights unclear; never copy upstream without consent. Rollback by returning to baseline Factory commit `29b9653ccbc4bcd36a190f9e9d78954bcc4dae76`; main, original EAI/SMAX/PREP, production and user data untouched.
