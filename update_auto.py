#!/usr/bin/env python3
# FPRS Auto Updater - גרסה חסינה לדוחות בורסה עם כותרות משובשות
import json, statistics, sys
from pathlib import Path
import pandas as pd
from collections import defaultdict

BASE = Path(__file__).parent
INCOMING = BASE / "data" / "incoming"
OUTPUT = BASE / "data" / "output" / "funds.json"
FRONTEND = BASE / "frontend" / "public" / "funds.json"

def find_header_row(df_raw):
    # מחפש שורה שמכילה "מספר קרן" / "שם קרן" / "תשואה"
    keywords = ['מספר', 'שם קרן', 'תשואה', 'קטגוריה', 'שארפ']
    for idx, row in df_raw.iterrows():
        row_str = ' '.join([str(v) for v in row.values])
        hits = sum(1 for k in keywords if k in row_str)
        if hits >= 2:
            return idx
    return 2 # fallback

def load_excel_smart(path):
    df_raw = pd.read_excel(path, header=None, nrows=20)
    h_row = find_header_row(df_raw)
    print(f"זוהתה שורת כותרת: {h_row}")
    df = pd.read_excel(path, header=h_row)
    df = df.dropna(how='all')
    # ניקוי עמודות Unnamed
    df.columns = [str(c).strip().replace('\xa0','') for c in df.columns]
    print(f"עמודות אמיתיות: {list(df.columns[:12])}")
    # מיפוי
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if 'מספר' in c or 'מס. קרן' in c: col_map['id'] = c
        elif 'שם' in c and 'קרן' in c: col_map['name'] = c
        elif 'קטגור' in c or 'סיווג' in c: col_map['category'] = c
        elif '12' in c and 'תשואה' in c:
            if 'ret_12m' not in col_map: col_map['ret_12m'] = c
        elif '36' in c and 'תשואה' in c: col_map['ret_36m'] = c
        elif 'שארפ' in cl or 'sharpe' in cl: col_map['sharpe'] = c
    # fallback לפי מיקום נפוץ בדוחות בורסה
    if 'id' not in col_map: col_map['id'] = df.columns[0]
    if 'name' not in col_map: col_map['name'] = df.columns[1] if len(df.columns)>1 else df.columns[0]
    if 'category' not in col_map and len(df.columns)>3: col_map['category'] = df.columns[3]
    print(f"מיפוי: {col_map}")
    return df, col_map

def load_old_json(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(data, dict) and 'funds' in data: data = data['funds']
    return {str(f.get('id','')): f for f in data if isinstance(f, dict) and f.get('id')}

def build(path_old, path_new, path_out):
    old = load_old_json(path_old) if Path(path_old).exists() else {}
    print(f"ישן: {len(old)} קרנות")
    df, cmap = load_excel_smart(path_new)
    print(f"חדש: {len(df)} שורות")

    cats = defaultdict(list)
    for _, r in df.iterrows():
        try:
            cat = str(r[cmap['category']]).strip() if 'category' in cmap else 'כללי'
            ret = float(r[cmap['ret_12m']]) if pd.notna(r.get(cmap.get('ret_12m'))) else 0
            cats[cat].append(ret)
        except: pass
    medians = {k: statistics.median(v) for k,v in cats.items() if v}

    new_funds=[]
    for _, r in df.iterrows():
        try:
            fid = str(r[cmap['id']]).strip()
            if not fid or fid=='nan': continue
            name = str(r[cmap['name']]).strip()
            cat = str(r[cmap.get('category', 'כללי')]).strip() if 'category' in cmap else 'כללי'
            ret12 = float(r[cmap['ret_12m']]) if 'ret_12m' in cmap and pd.notna(r[cmap['ret_12m']]) else 0
            ret36 = float(r[cmap['ret_36m']]) if 'ret_36m' in cmap and pd.notna(r.get(cmap['ret_36m'],0)) else ret12*2.8
            sharpe = float(r[cmap['sharpe']]) if 'sharpe' in cmap and pd.notna(r.get(cmap['sharpe'],0)) else 0.3
            median = medians.get(cat,0)
            score = 50 + (ret12-median)*25 + sharpe*6 if 'כספית' in cat else 50 + (ret12-median)*3.5 + sharpe*8
            new_funds.append({'id':fid,'name':name,'category':cat,'ret_12m':ret12,'ret_36m':ret36,'sharpe_12m':sharpe,'peer_median':median,'score':max(0,min(100,score))})
        except: pass

    for cat in set(f['category'] for f in new_funds):
        fl = [f for f in new_funds if f['category']==cat]
        fl.sort(key=lambda x:x['score'],reverse=True)
        for i,f in enumerate(fl):
            pct=(i+1)/len(fl)
            f['stars_count']=5 if pct<=0.1 else 4 if pct<=0.3 else 3 if pct<=0.5 else 2 if pct<=0.75 else 1
            f['rank']=i+1

    new_funds.sort(key=lambda x:x['score'],reverse=True)
    Path(path_out).parent.mkdir(parents=True,exist_ok=True)
    Path(path_out).write_text(json.dumps(new_funds,ensure_ascii=False,indent=2),encoding='utf-8')
    if FRONTEND.parent.exists():
        FRONTEND.write_text(json.dumps(new_funds,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"✅ נוצר {path_out} עם {len(new_funds)} קרנות")
    return new_funds

if __name__ == "__main__":
    latest = max([p for p in INCOMING.glob("*.xlsx") if not p.name.startswith("~$")], key=lambda p:p.stat().st_mtime) if not sys.argv[1:] else Path(sys.argv[1])
    print(f"מקור: {latest.name}")
    build(OUTPUT, latest, OUTPUT)
