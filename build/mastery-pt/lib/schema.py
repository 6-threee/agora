from dataclasses import dataclass

@dataclass
class Card:
    front: str
    back: str
    example: str = ""
    exampleEn: str = ""

def assign_ids(cards):
    out = []
    for i, c in enumerate(cards, 1):
        out.append({
            "id": f"ptm-{i:04d}",
            "front": c.front,
            "back": c.back,
            "example": c.example,
            "exampleEn": c.exampleEn,
        })
    return out

def validate(cards):
    errs = []
    seen_front, seen_id = set(), set()
    for c in cards:
        cid = c.get("id", "?")
        if not c.get("front", "").strip():
            errs.append(f"empty front on {cid}")
        if not c.get("back", "").strip():
            errs.append(f"empty back on {cid}")
        f = c.get("front", "")
        if f in seen_front:
            errs.append(f"duplicate front: {f!r} ({cid})")
        seen_front.add(f)
        if cid in seen_id:
            errs.append(f"duplicate id: {cid}")
        seen_id.add(cid)
    return errs
