
import pandas as pd
def hit_rate(monthly_returns):
    if not monthly_returns: return 0.5
    return sum(1 for r in monthly_returns if r>0)/len(monthly_returns)
def fee_zscore(fee, category_fees):
    if fee is None or len(category_fees)<2: return 0
    mean=pd.Series(category_fees).mean()
    std=pd.Series(category_fees).std()
    return (fee-mean)/std if std!=0 else 0
