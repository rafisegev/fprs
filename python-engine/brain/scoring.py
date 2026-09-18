"""
FundBrain - תיקון דירוג קטגוריאלי
התיקון: כל חישוב Z-Score ו-Percentile נעשה בתוך קבוצת category בלבד
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path

class FundBrain:
    DEFAULT_WEIGHTS = {
        "wM": 0.30,
        "wS": 0.25,
        "wD": 0.15,
        "wA": 0.20,
        "wF": 0.10,
    }

    def zscore_per_category(self, df: pd.DataFrame, col: str) -> pd.Series:
        return df.groupby('category')[col].transform(
            lambda x: (x - x.mean()) / (x.std() if x.std() and x.std()!= 0 else 1.0)
        )

    def score_from_fixed_json(self, json_path: str = "frontend/public/funds.json"):
        path = Path(json_path)
        if not path.exists():
            path = Path(__file__).parents[2] / "frontend" / "public" / "funds.json"

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        for col in ['return_1m','return_1y','return_3y','std_12','sharpe_12','excess_vs_peer_1y','fee']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # ===== התיקון - Z קטגוריאלי בלבד =====
        df['ZM'] = self.zscore_per_category(df, 'return_1y')
        df['ZS'] = self.zscore_per_category(df, 'sharpe_12')
        df['ZA'] = self.zscore_per_category(df, 'excess_vs_peer_1y')
        df['ZD'] = self.zscore_per_category(df, 'std_12')
        df['ZF'] = self.zscore_per_category(df, 'fee')

        w = self.DEFAULT_WEIGHTS
        df['Raw_Score'] = (
            w['wM'] * df['ZM'] +
            w['wS'] * df['ZS'] +
            w['wA'] * df['ZA'] -
            w['wD'] * df['ZD'] -
            w['wF'] * df['ZF']
        )

        # אחוזון סופי בתוך קטגוריה בלבד 0-100
        df['Final_Score'] = df.groupby('category')['Raw_Score'].transform(
            lambda x: x.rank(pct=True) * 100
        )

        def stars(p):
            if p >= 90: return "⭐⭐⭐⭐⭐"
            if p >= 67.5: return "⭐⭐⭐⭐"
            if p >= 32.5: return "⭐⭐⭐"
            if p >= 10: return "⭐⭐"
            return "⭐"

        df['Stars'] = df['Final_Score'].apply(stars)
        df['rank_in_category'] = df.groupby('category')['Final_Score'].rank(ascending=False, method='min').astype(int)
        return df

    def save(self, df: pd.DataFrame, out_path: str = "frontend/public/funds.json"):
        records = df.to_dict(orient='records')
        for r in records:
            r['score'] = round(float(r['Final_Score']), 1)
            r['stars'] = r['Stars']

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅ נשמר {len(records)} קרנות עם דירוג קטגוריאלי ל-{out_path}")

if __name__ == "__main__":
    brain = FundBrain()
    base = Path.cwd()
    if base.name == "python-engine":
        base = base.parent
    json_path = base / "frontend" / "public" / "funds.json"
    df = brain.score_from_fixed_json(str(json_path))
    brain.save(df, str(json_path))
    print(df['Stars'].value_counts())
