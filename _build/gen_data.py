# Regenerates assets/js/data.js with placeholder units.
# Run from the folder ABOVE `rezidencia/`.  ⚠️ OVERWRITES data.js.
import json, random
random.seed(7)

# floor -> (units, bay_offset) ; base building is 7 bays wide
PLAN = {1:(7,0), 2:(7,0), 3:(7,0), 4:(7,0), 5:(7,0), 6:(7,0), 7:(5,1), 8:(3,2)}

LAYOUTS = {
 "A": ("1-izbový byt", 1, (33,42), (4,8)),
 "B": ("2-izbový byt", 2, (48,58), (6,12)),
 "C": ("2-izbový byt", 2, (59,67), (8,16)),
 "D": ("3-izbový byt", 3, (72,84), (9,18)),
 "E": ("3-izbový byt", 3, (85,95), (12,24)),
 "F": ("4-izbový byt", 4, (102,124), (14,28)),
 "G": ("Penthouse", 5, (142,178), (38,72)),
}
# bay index -> layout mix for standard floors
BAY_LAYOUT = ["B","D","A","E","A","D","C"]
ORIENT = ["Juh","Juhozápad","Západ","Sever","Severovýchod","Východ","Juhovýchod"]
BAY_ORIENT = ["Juhozápad","Juh","Juh","Juhovýchod","Východ","Severovýchod","Sever"]

ROOMS_BY_TYPE = {
 1: [("Predsieň",5.2),("Obytná miestnosť s kuchyňou",22.0),("Kúpeľňa s WC",4.4)],
 2: [("Predsieň",7.0),("Obývacia izba s kuchyňou",28.0),("Spálňa",14.2),("Kúpeľňa",5.0),("WC",1.8)],
 3: [("Predsieň",8.1),("Obývacia izba s kuchyňou",33.5),("Spálňa",15.4),("Izba",12.6),("Chodba",4.2),("Kúpeľňa",6.0),("WC",2.0)],
 4: [("Predsieň",9.4),("Obývacia izba s kuchyňou",38.0),("Spálňa",17.2),("Izba",13.8),("Izba",12.1),("Chodba",5.6),("Kúpeľňa",6.8),("Kúpeľňa s WC",4.9),("Šatník",3.4)],
 5: [("Vstupná hala",12.0),("Obývacia izba s kuchyňou",52.0),("Spálňa",22.4),("Izba",16.2),("Izba",14.8),("Pracovňa",11.0),("Chodba",7.4),("Kúpeľňa",9.2),("Kúpeľňa s WC",6.1),("Šatník",5.5),("Technická miestnosť",4.0)],
}

def status_for(i):
    r = random.random()
    if r < 0.24: return "predany"
    if r < 0.40: return "rezervovany"
    return "dostupny"

apts = []
for floor, (count, off) in PLAN.items():
    for k in range(count):
        bay = off + k
        if floor == 8:
            code = "G"
        elif floor == 7:
            code = ["D","F","A","F","C"][k]
        else:
            code = BAY_LAYOUT[bay]
        name, rooms, area_r, ext_r = LAYOUTS[code]
        area = round(random.uniform(*area_r), 2)
        ext = round(random.uniform(*ext_r), 2)
        ext_kind = "Terasa" if floor >= 7 else ("Balkón" if floor > 1 else "Predzáhradka")
        ppm = 4180 + (floor - 1) * 95 + (140 if code == "G" else 0)
        price = int(round((area * ppm + ext * ppm * 0.42) / 100.0) * 100)
        st = "dostupny" if floor == 1 and k == 0 else status_for(len(apts))
        # room breakdown scaled to the actual area
        base = ROOMS_BY_TYPE[rooms]
        tot = sum(a for _, a in base)
        scale = area / tot
        rr = [{"name": n, "area": round(a * scale, 1)} for n, a in base]
        apts.append({
            "id": f"{floor}.{k+1:02d}",
            "floor": floor, "bay": bay, "bays": count, "bayOffset": off,
            "layout": code, "type": name, "rooms": rooms,
            "area": area, "ext": ext, "extKind": ext_kind,
            "total": round(area + ext, 2),
            "orientation": "Juh / Západ" if code == "G" else BAY_ORIENT[bay],
            "status": st, "price": price,
            "roomList": rr,
        })

lines = []
for a in apts:
    lines.append("  " + json.dumps(a, ensure_ascii=False, separators=(", ", ": ")))
body = ",\n".join(lines)

header = '''/* ---------------------------------------------------------------------------
 * REZIDENCIA AURORA — apartment data
 *
 * ⚠️  DEMO / PLACEHOLDER DATA — replace every record with the real unit list.
 *     Keep the field names, everything on the site reads from this one file.
 *
 *   id          "4.03"  — unit code (floor.index), also used in the URL
 *   floor       1-8
 *   bay         0-6     — horizontal position in the facade (0 = left)
 *   bays        how many units sit on this floor
 *   bayOffset   left offset of this floor's slab (upper floors are set back)
 *   layout      "A"-"G" — layout/typologia code
 *   type        human label ("3-izbový byt")
 *   rooms       number of rooms
 *   area        interior m²
 *   ext         exterior m² (balcony / terrace / garden)
 *   extKind     "Balkón" | "Terasa" | "Predzáhradka"
 *   orientation compass orientation
 *   status      "dostupny" | "rezervovany" | "predany"
 *   price       € incl. VAT — set to null to render "Cena na vyžiadanie"
 *   roomList    per-room breakdown for the detail page
 * ------------------------------------------------------------------------ */

/* Set to false before launch if prices should not be public yet. */
const SHOW_PRICES = true;

const BUILDING = {
  name: "Rezidencia Aurora",
  street: "Placeholder 12",
  city: "Bratislava",
  district: "Staré Mesto",
  floors: 8,
  bays: 7,
  totalUnits: 50,
};

const APARTMENTS = [
'''

with open("rezidencia/assets/js/data.js", "w") as f:
    f.write(header + body + "\n];\n")

print("units:", len(apts))
from collections import Counter
print(Counter(a["status"] for a in apts))
print(Counter(a["rooms"] for a in apts))
