from pathlib import Path
import pandas as pd, json
from datetime import datetime
from src.loader import load_any
from src.preprocessing import synthetic_nav_from_returns
from src.engines.momentum import momentum_score
from src.engines.risk import sortino_ratio, max_drawdown
from src.engines.alpha import excess_return
from src.decay_detection import detect_momentum_deceleration, decay_penalty, decay_flag
from src.scoring import WEIGHTS
from src.rating import star_rating_and_label, quality_system_label
BASE=Path(__file__).parent.parent
IN=BASE/"data"/"incoming"
OUT=BASE/"data"/"output"
OUT.mkdir(parents=True, exist_ok=True)
def run_pipeline():
    files=list(IN.glob("*.xls"))+list(IN.glob("*.xlsx"))
    if not files:
        print("❌ אין קובץ ב-data/incoming")
        return
    latest=max(files, key=lambda p: p.stat().st_mtime)
    print(f"📁 מעבד: {latest.name}")
    df=load_any(latest)
    records=[]
    for _, row in df.iterrows():
        nav=synthetic_nav_from_returns(row.get("Return_1Y"), row.get("Return_3Y"), 36)
        mom=momentum_score(nav) if nav else (row.get("Return_1Y") or 0)/10
        sortino=row.get("Sharpe_1Y") or row.get("Sharpe") or 0
        sharpe_3y=row.get("Sharpe_3Y") or sortino
        alpha=excess_return(row.get("Return_1Y"), 5)
        dec_trig,_=detect_momentum_deceleration(nav) if nav else (False,0)
        penalty=decay_penalty(dec_trig)
        ret_1m = row.get("Return_1M") or (row.get("Return_1Y")/12 if row.get("Return_1Y") else None)
        records.append({**row.to_dict(), "NAV_Series":nav, "Momentum":mom, "Sortino":sortino, "Sharpe_1Y_val":sortino, "Sharpe_3Y_val":sharpe_3y, "Return_1M_val":ret_1m, "MaxDD":0, "Alpha":alpha, "Consistency":0.6, "IsDecay":dec_trig, "DecayPenalty":penalty})
    df2=pd.DataFrame(records)
    for col,zcol in [("Momentum","Z_M"),("Sortino","Z_S"),("MaxDD","Z_D"),("Alpha","Z_A"),("Consistency","Z_C")]:
        df2[zcol]=df2.groupby("Category")[col].transform(lambda x: (x-x.mean())/x.std() if x.std()!=0 and len(x)>1 else 0)
    df2["Z_F"]=df2.groupby("Category")["Management_Fee"].transform(lambda x: (x-x.mean())/x.std() if x.std()!=0 and len(x)>1 else 0)
    df2["RawScore"]=df2.apply(lambda r: WEIGHTS["momentum"]*r["Z_M"]+WEIGHTS["sortino"]*r["Z_S"]-WEIGHTS["drawdown"]*r["Z_D"]+WEIGHTS["alpha"]*r["Z_A"]+WEIGHTS["consistency"]*r["Z_C"]-WEIGHTS["fee"]*r["Z_F"], axis=1)
    df2["FinalScore"]=pd.Series(df2["RawScore"]).rank(pct=True)*100 * df2["DecayPenalty"]
    df2["FinalScore"]=df2["FinalScore"].clip(0,100)
    df2[["Stars","StarsDesc"]]=df2["FinalScore"].apply(lambda s: pd.Series(star_rating_and_label(s)))
    df2["QualityLabel"]=df2["FinalScore"].apply(quality_system_label)
    df2["DecayFlag"]=df2["IsDecay"].apply(decay_flag)
    df2=df2.sort_values("FinalScore", ascending=False)
    df2["Rank"]=range(1,len(df2)+1)
    funds=[]
    for _, r in df2.iterrows():
        funds.append({"id":str(r["Fund_ID"]), "name":str(r["Fund_Name"]), "category":str(r["Category"]), "mgmt_fee":r.get("Management_Fee"), "return_1m": r.get("Return_1M_val"), "return_1y":r.get("Return_1Y"), "return_12m":r.get("Return_1Y"), "return_3y":r.get("Return_3Y"), "return_36m":r.get("Return_3Y"), "sharpe_1y": r.get("Sharpe_1Y_val"), "sharpe_3y": r.get("Sharpe_3Y_val"), "score":round(float(r["FinalScore"]),2), "rank":int(r["Rank"]), "quality_label":r["QualityLabel"], "stars":int(r["Stars"]), "stars_desc": str(r["StarsDesc"]), "decay_flag":r["DecayFlag"], "is_decay":bool(r["IsDecay"])})
    out={"last_updated":datetime.now().isoformat(), "total_funds":len(funds), "model_weights":WEIGHTS, "funds":funds}
    with open(OUT/"funds.json","w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=2)
    flat=Path(BASE/"frontend"/"public"/"funds.json")
    flat.parent.mkdir(parents=True, exist_ok=True)
    with open(flat,"w",encoding="utf-8") as f: json.dump(funds,f,ensure_ascii=False,indent=2)
    print(f"✅ {len(funds)} קרנות")
if __name__=="__main__":
    run_pipeline()
