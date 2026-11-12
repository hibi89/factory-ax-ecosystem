# Factory AX VERIFY W1 owner candidate — dependencies & rights inventory

2026-11-12 KST. Scope: **source-only developer QA bundle**, not approved sale/licensed redistribution.

| Component | Source / dependency | Rights and verification status |
|---|---|---|
| FactoryAX verify/reconcile/delivery/backup/gui | Original locally authored code in this private Factory AX repository; Python 3.11+ standard library | Customer sale/license terms, liability/support, authorship and signing not finally approved; RELEASE HOLD |
| Packaging scripts/tests | Original Factory AX source; `zipfile`, `tkinter`, `unittest`, `hashlib`, `csv` etc. stdlib | Requires separately installed compatible Python and Tk support; Windows runtime compatibility not proven |
| Supplier profile draft HTML | Original local HTML in Factory AX; no CDN or external libraries | Local browser owner UI does **not** constitute authenticated approval |
| PREP / SMAX² | Contract inspiration only; **no upstream code bundled** | Upstream source/license/commercial redistribution and golden parity not established |
| EAI / DBVORA / HAE / LA / SOVIA | No source/runtime bundled or imported | Feature integration, version/permission contracts and license review still due |
| Synthetic demo/test fixtures | Invented production/quality/shipment examples only | No customer data, commercial claims, passwords, actual production inputs or secrets |
| OS/Python distribution | Python not included, OS not included | Customer runtime deployment/defender/signing/provenance not assessed |

No third-party Python packages are required by the package at build/runtime. Standard-library source availability does **not** settle Python installer redistribution rights or the product's license. Signed executable and customer NDA/rights/NOTICE inventory must be reviewed before shipping.
