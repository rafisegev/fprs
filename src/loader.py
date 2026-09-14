
import pandas as pd
from pathlib import Path
def clean_number(v):
    if pd.isna(v): return None
    s=str(v).replace("%","").replace(",","").strip()
    try: return float(s)
    except: return None
def norm_id(v):
    if pd.isna(v): return ""
    s=str(v).strip()
    try:
        f=float(s)
        return str(int(f)) if f.is_integer() else s
    except: return s
def load_fundd(path):
    df=pd.read_excel(path, sheet_name="be-rank-funds", header=0)
    out=pd.DataFrame()
    out["Fund_ID"]=df["מספר נייר"].apply(norm_id) if "מספר נייר" in df.columns else df["מזהה"].apply(norm_id)
    out["Fund_Name"]=df["שם קרן"] if "שם קרן" in df.columns else ""
    out["Category"]=df["קטגוריה"] if "קטגוריה" in df.columns else "כללי"
    out["Management_Fee"]=df["שכר מנהל ונאמן"].apply(clean_number) if "שכר מנהל ונאמן" in df.columns else None
    out["Return_1Y"]=df["תשואה - שנה אחרונה"].apply(clean_number)
    out["Return_3Y"]=df["תשואה - 3 שנים אחרונות"].apply(clean_number)
    out["Sharpe_1Y"]=df["שארפ - שנה אחרונה"].apply(clean_number)
    out["AUM"]=df["נכס מנוהל (מ)"].apply(clean_number)
    out["Benchmark_ID"]=df["מדד ייחוס"] if "מדד ייחוס" in df.columns else out["Category"]
    return out
def load_new(path):
    raw=pd.read_excel(path, header=None)
    hi=None
    for i in range(10):
        if any("מספר קרן" in str(v) for v in raw.iloc[i].tolist()):
            hi=i; break
    if hi is None: hi=6
    data=raw.iloc[hi+1:].copy()
    out=pd.DataFrame()
    out["Fund_ID"]=data.iloc[:,0].apply(norm_id)
    out["Fund_Name"]=data.iloc[:,1].astype(str)
    out["Return_1M"]=data.iloc[:,2].apply(clean_number)
    out["Return_1Y"]=data.iloc[:,5].apply(clean_number)
    out["Sharpe_1Y"]=data.iloc[:,7].apply(clean_number)
    out["Return_3Y"]=data.iloc[:,8].apply(clean_number)
    out["Management_Fee"]=data.iloc[:,13].apply(clean_number)
    out["AUM"]=data.iloc[:,14].apply(clean_number)
    out["Category"]="כללי"
    out["Benchmark_ID"]="כללי"
    return out
def load_any(path):
    p=Path(path)
    if p.suffix==".xls":
        return load_fundd(p)
    try:
        xls=pd.ExcelFile(p)
        if "be-rank-funds" in xls.sheet_names:
            return load_fundd(p)
    except: pass
    return load_new(p)
