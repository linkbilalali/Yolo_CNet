# conceptnet.py
# =============
# ConceptNet local database se object ki information nikalta hai.
# Yeh file sirf ek function deti hai: get_info(label)
# Is file ko directly nahi chalate - yolo.py isko import karta hai.

import sqlite3
from pathlib import Path

# Tumhara local ConceptNet database yahan hoga (setup_conceptnet.py chala kar banaya tha)
DB_PATH = Path.home() / "conceptnet_data" / "conceptnet.db"

# Sirf yeh relations chahiye humein
RELATIONS = {
    "/r/IsA"           : "is a",
    "/r/UsedFor"       : "used for",
    "/r/AtLocation"    : "found at",
    "/r/CapableOf"     : "capable of",
    "/r/ReceivesAction": "receives action",
}


def get_info(label: str) -> dict:
    """
    Ek object label dو, ConceptNet se uski info milti hai.

    Example:
        get_info("cup")
        >> { "is a": ["container", "vessel"], "used for": ["drinking"] }

    Args:
        label : YOLO ka object naam, e.g. "cup", "laptop", "person"

    Returns:
        dict of { relation: [concepts] }
        Ya empty {} agar database nahi mila ya object unknown hai.
    """

    # Pehle check karo database exist karta hai
    if not DB_PATH.exists():
        print("[ConceptNet] ERROR: Database nahi mila!")
        print(f"[ConceptNet] Pehle setup_conceptnet.py chalao. Path: {DB_PATH}")
        return {}

    # Label ko ConceptNet URI format mein convert karo
    # e.g.  "cell phone"  ->  "/c/en/cell_phone"
    uri = "/c/en/" + label.strip().lower().replace(" ", "_")

    found = {}

    try:
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for rel_uri, rel_name in RELATIONS.items():

            # Database mein dhundho jahan humara object START node ho
            cursor.execute("""
                SELECT end, weight
                FROM edges
                WHERE start = ? AND relation = ?
                ORDER BY weight DESC
                LIMIT 3
            """, (uri, rel_uri))

            rows = cursor.fetchall()

            if rows:
                # URI se readable naam nikalo
                # "/c/en/drinking_liquid"  ->  "drinking liquid"
                concepts = []
                for (end_uri, _) in rows:
                    parts = end_uri.split("/")
                    if len(parts) >= 4:
                        concepts.append(parts[3].replace("_", " "))
                found[rel_name] = concepts

        conn.close()

    except Exception as e:
        print(f"[ConceptNet] Query error: {e}")

    return found