import numpy as np

def slope_and_r2(nav_series):
    if nav_series is None or len(nav_series) < 5: 
        return 0, 0
    x = np.arange(len(nav_series))
    y = np.array(nav_series)
    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    ss_res = ((y - y_pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    return slope, r2

def momentum_score(nav_series, weights={3:0.2, 6:0.3, 12:0.5}):
    if nav_series is None: 
        return 0
    total = 0
    for months, w in weights.items():
        window = nav_series[-months:] if len(nav_series) >= months else nav_series
        slope, r2 = slope_and_r2(window)
        total += w * slope * r2
    return total
