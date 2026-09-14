
import pandas as pd
def clean_number(val):
    if pd.isna(val): return None
    s=str(val).replace("%","").replace(",","").strip()
    try: return float(s)
    except: return None
def synthetic_nav_from_returns(return_1y, return_3y, months=36):
    if return_1y is None and return_3y is None: return None
    base=100.0
    if return_1y:
        monthly=(1+return_1y/100)**(1/12)-1 if return_1y>-100 else 0
    else:
        monthly=(return_3y/100/3)/12 if return_3y else 0
    return [base * (1+monthly)**i for i in range(months)]
