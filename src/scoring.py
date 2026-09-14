
import pandas as pd
WEIGHTS = {"momentum":0.30, "sortino":0.20, "drawdown":0.10, "alpha":0.25, "consistency":0.10, "fee":0.15}
def calculate_raw_score(row):
    return (
        WEIGHTS["momentum"]*row.get("Z_M",0) +
        WEIGHTS["sortino"]*row.get("Z_S",0) -
        WEIGHTS["drawdown"]*row.get("Z_D",0) +
        WEIGHTS["alpha"]*row.get("Z_A",0) +
        WEIGHTS["consistency"]*row.get("Z_C",0) -
        WEIGHTS["fee"]*row.get("Z_F",0)
    )
def final_score_with_decay(raw_scores, decay_penalties):
    percentiles = pd.Series(raw_scores).rank(pct=True)*100
    final = percentiles * pd.Series(decay_penalties)
    return final.clip(0,100)
