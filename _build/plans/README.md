# Floor plan pipeline

Source of truth for every apartment number on the site.

    src/1np.pdf, src/2 az 4 np.pdf, src/5np.pdf   architect's vector drawings
        │
        ├─ genplans.py  → ../../assets/plans/*.svg   (26 per-apartment plans)
        │                  + plans_meta.json         (room codes → areas)
        │
        └─ gendata.py   → data.js                    (copy to ../../assets/js/)

Run from this folder, with `pymupdf` installed:

```bash
python3 genplans.py && python3 gendata.py
cp data.js ../../assets/js/data.js
```

`genplans.py` holds the clip rectangle per apartment (`CROP`) in the PDF's
unrotated coordinate space, and `SCHEMA` maps the architect's room codes to
display names and merged areas. If the architect sends revised drawings, check
the crops first — `CROP` assumes the party walls stay where they are.

Room names are inferred from the fixtures drawn on the plan; the PDFs carry
codes and areas only, no room names.
