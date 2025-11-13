import pandas as pd

def safe_parse(val):
    if pd.isnull(val): return 0
    s = str(val).replace('<','').replace('>','')
    if '-' in s:
        try:
            return float(s.split('-')[0])
        except:
            return 0
    try:
        return float(s)
    except:
        return 0

def classify_water_type(row):
    bod = safe_parse(row.get("bod"))
    tss = safe_parse(row.get("tss"))
    nitrate = safe_parse(row.get("nitrate"))
    phosphate = safe_parse(row.get("phosphate"))

    if nitrate > 1000 or phosphate > 100 or bod > 1000:
        return "Yellow Water"
    elif bod >= 300 and tss >= 250 and nitrate >= 40:
        return "Black Water"
    elif bod >= 200 and bod < 600 and tss >= 200 and nitrate >= 30 and nitrate < 100:
        return "Brown Water"
    elif bod < 300 and tss < 300 and nitrate < 30:
        return "Grey Water"
    else:
        return "Unknown"
# Filtering and scoring logic