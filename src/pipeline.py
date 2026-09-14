
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
        print("❌ אין קובץ ב-data/incoming - תעתיק קובץ אקסל לשם")
        return
    latest=max(files, key=lambda p: p.stat().st_mtime)
    print(f"📁 מעבד: {latest.name}")
    df=load_any(latest)
    print(f"📊 {len(df)} קרנות נטענו - עמודות: {list(df.columns)}")
    records=[]
    for _, row in df.iterrows():
        nav=synthetic_nav_from_returns(row.get("Return_1Y"), row.get("Return_3Y"), 36)
        mom=momentum_score(nav) if nav else (row.get("Return_1Y") or 0)/10
        sortino=row.get("Sharpe_1Y") or 0
        alpha=excess_return(row.get("Return_1Y"), 5)
        dec_trig,_=detect_momentum_deceleration(nav) if nav else (False,0)
        penalty=decay_penalty(dec_trig)
        records.append({**row.to_dict(), "NAV_Series":nav, "Momentum":mom, "Sortino":sortino, "MaxDD":0, "Alpha":alpha, "Consistency":0.6, "IsDecay":dec_trig, "DecayPenalty":penalty})
    df2=pd.DataFrame(records)
    # Z-Score per Category
    for col,zcol in [("Momentum","Z_M"),("Sortino","Z_S"),("MaxDD","Z_D"),("Alpha","Z_A"),("Consistency","Z_C")]:
        df2[zcol]=df2.groupby("Category")[col].transform(lambda x: (x-x.mean())/x.std() if x.std()!=0 and len(x)>1 else 0)
    df2["Z_F"]=df2.groupby("Category")["Management_Fee"].transform(lambda x: (x-x.mean())/x.std() if x.std()!=0 and len(x)>1 else 0)
    # Raw Score
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
        funds.append({"id":str(r["Fund_ID"]), "name":str(r["Fund_Name"]), "category":str(r["Category"]), "mgmt_fee":r.get("Management_Fee"), "return_1y":r.get("Return_1Y"), "return_3y":r.get("Return_3Y"), "score":round(float(r["FinalScore"]),2), "rank":int(r["Rank"]), "percentile":round(float(r["FinalScore"]),1), "quality_label":r["QualityLabel"], "stars":r["Stars"], "decay_flag":r["DecayFlag"], "is_decay":bool(r["IsDecay"]), "momentum":round(float(r["Momentum"]),4), "alpha":round(float(r["Alpha"]),2)})
    out={"last_updated":datetime.now().isoformat(), "total_funds":len(funds), "model_weights":WEIGHTS, "funds":funds}
    out_path=OUT/"funds.json"
    with open(out_path,"w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=2)
    print(f"✅ נוצר {out_path} עם {len(funds)} קרנות")
    # גם flat לאתר הישן
    flat_path=Path(BASE/"frontend"/"public"/"funds.json")
    flat_path.parent.mkdir(parents=True, exist_ok=True)
    with open(flat_path,"w",encoding="utf-8") as f: json.dump(funds,f,ensure_ascii=False,indent=2)
    print(f"✅ נוצר גם {flat_path} לאתר Vercel")
    return out_path

if __name__=="__main__":
    run_pipeline()
