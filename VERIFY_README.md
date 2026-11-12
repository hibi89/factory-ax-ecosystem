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
