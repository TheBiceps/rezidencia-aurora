# -*- coding: utf-8 -*-
"""Build assets/js/data.js from the architect's PDFs. Source of truth: plans_meta.json."""
import json, io
M = json.load(open("plans_meta.json"))

LIV = "Obývacia izba s kuchyňou"
STU = "Obytná izba s kuchyňou"
# (display name, [architect room codes]) in display order
SCHEMA = {
 "A": [(LIV,[3,4]),("Spálňa",[5]),("Predsieň",[1]),("Kúpeľňa",[6]),("WC",[2])],
 "B": [(LIV,[3,4]),("Spálňa",[5]),("Predsieň",[1]),("Kúpeľňa",[6]),("WC",[2])],
 "C": [(LIV,[4,5]),("Spálňa",[3]),("Predsieň",[1]),("Kúpeľňa",[2])],
 "D": [(LIV,[5,6]),("Spálňa",[4]),("Šatník",[3]),("Predsieň",[1]),("Kúpeľňa",[2])],
 "E": [(STU,[1,3]),("Kúpeľňa",[2])],
 "F": [(STU,[1,3]),("Kúpeľňa",[2])],
 "G": [(STU,[1,3]),("Kúpeľňa",[2])],
 "H": [(LIV,[4,5]),("Spálňa",[6]),("Spálňa",[7]),("Predsieň",[1]),("Kúpeľňa",[2]),("Komora",[3])],
 "I": [(LIV,[4,5]),("Spálňa",[6]),("Spálňa",[7]),("Predsieň",[1]),("Kúpeľňa",[2]),("Komora",[3])],
}
ROOMS_N = {"A":2,"B":2,"C":2,"D":2,"E":1,"F":1,"G":1,"H":3,"I":3}
TYPE = {1:"1-izbový byt",2:"2-izbový byt",3:"3-izbový byt"}
GROUP = {1:"1np",2:"24np",3:"24np",4:"24np",5:"5np"}
# facade bay index, ordered the way the flats actually sit along the building
# (left to right on the drawings). 1.NP has no I — that bay is the entrance lobby.
BAY = {"I":0,"H":1,"G":2,"F":3,"A":4,"E":5,"B":6,"D":7,"C":8}

out=[]
for floor in (1,2,3,4,5):
    g = GROUP[floor]
    for letter in sorted(M[g]):
        d = M[g][letter]
        rl=[]
        for name, codes in SCHEMA[letter]:
            a = round(sum(d["rooms"][str(c)] for c in codes), 1)
            rl.append({"name":name, "area":a, "codes":["%d.%s.%d"%(floor,letter,c) for c in codes]})
        interior = round(sum(r["area"] for r in rl), 1)
        assert abs(interior - d["interior"]) < 0.05, (floor,letter,interior,d["interior"])
        bal = d["balcony"]
        out.append({
            "id":"%d.%s"%(floor,letter), "floor":floor, "letter":letter,
            "bay":BAY[letter], "bays":9, "bayOffset":0,
            "plan":"assets/plans/plan-%s-%s.svg"%(g,letter),
            "type":TYPE[ROOMS_N[letter]], "rooms":ROOMS_N[letter],
            "area":interior, "ext":bal, "extKind":"Balkón",
            "total":round(interior+bal,1),
            "status":"dostupny", "price":None,
            "roomList":[{"name":r["name"],"area":r["area"]} for r in rl],
        })

hdr = '''/* ---------------------------------------------------------------------------
 * P6 — apartment data
 *
 * GENERATED FROM THE ARCHITECT'S FLOOR PLANS (1np.pdf, "2 az 4 np.pdf", 5np.pdf,
 * Ing. arch. Martin Krajči, podklad arch. Kullman). Room areas are the values
 * printed on those drawings; nothing here is invented.
 *
 * Per the architect's note, kitchen and living room are merged into a single
 * figure, and in one-room flats the entrance area is merged in as well —
 * the spaces run into one another and are not separated by walls.
 *
 * ⚠️  AREAS ARE INDICATIVE. The building is an existing skeleton being
 *     reconstructed; deviations of roughly ±5–10 cm are possible, which moves
 *     the areas. Balcony areas are not final. The investor reserves the right
 *     to changes. Keep the disclaimer visible wherever these numbers appear.
 *
 * STILL TO COME FROM THE CLIENT — do not invent:
 *   price        currently null everywhere -> renders "Cena na vyžiadanie"
 *   status       everything is "dostupny"; update as units get reserved/sold
 *   orientation  needs a site plan with a north arrow; the field, the filter
 *                and the compass were removed rather than guessed
 *   parking, cellars, standard of finish
 *
 *   id        "2.A"  floor + apartment letter, as labelled on the drawings
 *   floor     1-5    nadzemné podlažie
 *   letter    A-I    apartment within the floor (1.NP has no I — lobby)
 *   plan      per-apartment SVG cut from the architect's vector PDF
 *   area      interior m², sum of roomList
 *   ext       balcony m²
 *   roomList  merged rooms as printed on the plan
 * ------------------------------------------------------------------------ */

/* Set to false to hide prices entirely; with price:null each unit already
   renders "Cena na vyžiadanie". */
const SHOW_PRICES = true;

const BUILDING = {
  name: "P6",
  street: "Prievozská 6",
  city: "Bratislava",
  district: "Ružinov",
  floors: 5,
  units: %d,
  areaMin: %.1f,
  areaMax: %.1f,
  /* per-floor unit letters; 1.NP has no I — that is the entrance lobby */
  layout: { 1: "ABCDEFGH", 2: "ABCDEFGHI", 3: "ABCDEFGHI", 4: "ABCDEFGHI", 5: "ABCDEFGHI" },
};

const APARTMENTS = [
''' % (len(out), min(a["area"] for a in out), max(a["area"] for a in out))

def j(o):
    return json.dumps(o, ensure_ascii=False, separators=(", ", ": "))
body = ",\n".join("  "+j(a) for a in out)
open("data.js","w",encoding="utf-8").write(hdr+body+"\n];\n")
print("apartments:", len(out))
from collections import Counter
print("by floor:", dict(Counter(a["floor"] for a in out)))
print("by rooms:", dict(Counter(a["rooms"] for a in out)))
print("interior range: %.1f – %.1f" % (min(a["area"] for a in out), max(a["area"] for a in out)))
print("total range:    %.1f – %.1f" % (min(a["total"] for a in out), max(a["total"] for a in out)))
