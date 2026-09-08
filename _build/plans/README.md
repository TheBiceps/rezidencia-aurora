# Floor plan pipeline

Source of truth for every apartment number on the site, and for the plans the
apartment pages show.

    src/1np.pdf, src/2 az 4 np.pdf, src/5np.pdf   architect's vector drawings
        │
        ├─ gendata.py       → data.js                   (copy to ../../assets/js/)
        │                     reads plans_meta.json     (room codes → areas)
        │
    ~/Downloads/P6 Floor Plans/                   architect's rendered plans (PNG)
        │
        └─ import_renders.py → ../../assets/plans/*.webp

Run from this folder, with `pymupdf` and `pillow` installed:

```bash
python3 gendata.py && cp data.js ../../assets/js/data.js
python3 import_renders.py "~/Downloads/P6 Floor Plans"
```

## Two different drawings, two different jobs

The **PDFs** are the numbers: room codes and areas, and — importantly — the
apartment letter printed at each front door. Nothing else identifies which flat
is which. E, F and G are one-room flats that differ by 0,4 m² in total and are
mirror images of each other; no amount of looking at the renders will tell them
apart. Left to right along the courtyard side they run **G, F, E**.

The **renders** are what the visitor sees: furnished, shaded, labelled per room.
They arrive as one PNG per apartment plus one per storey. Two quirks:

* apartment **A** is drawn differently on each band, so it ships as
  `A1` / `A2-4` / `A5`; **B–I** are identical across 2.–5. NP and ship once.
* **1.NP has no apartment I** — that corner is the entrance lobby.

## The bit that will bite you

`import_renders.py` auto-trims every per-apartment render, but gives the two
full-storey plans a **fixed** crop (`FLOOR_CROP`). That is deliberate: the
clickable outlines in `assets/js/floorplan.js` are percentages of the *cropped*
storey plan. Re-crop the plan and every outline silently shifts. If new storey
renders arrive, either keep the crop identical or re-derive the outlines.

`gendata.py` asserts that each apartment's room areas sum to the interior area
on the drawing, so a bad edit fails loudly rather than shipping wrong numbers.
The rendered plans were cross-checked against it: all 44 units agree.

Room names are inferred from the fixtures drawn on the plan; the PDFs carry
codes and areas only, no room names.
