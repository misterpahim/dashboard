
import re
import sys
import pandas as pd
from collections import defaultdict

KEYS = {
    "OEE": [r"\bOEE\b", r"\bIND\.?\s*OEE%?\b", r"\bEfficiency\b"],
    "DT_DIE": [r"\bDIE\s*DOWNTIME\b"],
    "DT_PROD": [r"\bPRODUCTION\s*DOWNTIME\b"],
    "DT_MAINT": [r"\bMAINT(ENANCE)?\s*DOWNTIME\b"],
    "DT_ENG": [r"\bENGINEER(ING)?\s*DOWNTIME\b"],
    "DT_OTH": [r"\bOTHERS?\s*DOWNTIME\b"],
    "GOOD_PARTS": [r"\bTOTAL\s*GOOD\s*PARTS\b", r"\bGOOD\s*PARTS\b"],
}

def find_nearby_value(df, r, c, search_radius=3):
    # Search rightwards then below for first numeric
    for dc in range(1, search_radius+1):
        cc = c+dc
        if cc < df.shape[1]:
            val = df.iat[r, cc]
            if pd.api.types.is_number(val):
                return (r, cc, val)
    for dr in range(1, search_radius+1):
        rr = r+dr
        if rr < df.shape[0]:
            val = df.iat[rr, c]
            if pd.api.types.is_number(val):
                return (rr, c, val)
    return (None, None, None)

def scan_sheet(df):
    hits = defaultdict(list)
    for r in range(min(300, df.shape[0])):
        for c in range(min(60, df.shape[1])):
            v = df.iat[r, c]
            if not isinstance(v, str):
                continue
            s = v.strip().upper()
            for key, pats in KEYS.items():
                for pat in pats:
                    if re.search(pat, s, re.IGNORECASE):
                        rr, cc, val = find_nearby_value(df, r, c)
                        hits[key].append({"label_cell": (r, c), "value_cell": (rr, cc), "value": val})
                        break
    return hits

def to_excel_addr(r, c):
    if r is None or c is None: return None
    col = ""
    x = c+1
    while x:
        x, rem = divmod(x-1, 26)
        col = chr(65+rem) + col
    return f"{col}{r+1}"

def main():
    if len(sys.argv)<2:
        print("Usage: python discover_cells.py <excel_path>")
        sys.exit(1)
    path = sys.argv[1]
    xls = pd.ExcelFile(path)
    summary = {}
    for s in xls.sheet_names:
        if not s.isdigit():
            continue
        df = pd.read_excel(path, sheet_name=s, header=None)
        hits = scan_sheet(df)
        for k, arr in hits.items():
            for item in arr:
                item["label_addr"] = to_excel_addr(*item["label_cell"])
                item["value_addr"] = to_excel_addr(*item["value_cell"])
                item.pop("label_cell", None); item.pop("value_cell", None)
        summary[s] = hits
    import json
    print(json.dumps(summary, indent=2, default=str))

if __name__ == "__main__":
    main()
