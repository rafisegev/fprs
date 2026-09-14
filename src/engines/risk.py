
import numpy as np
def sortino_ratio(returns, rf=0.02):
    if returns is None or len(returns)<2: return 0
    excess = np.array(returns) - rf/12
    downside = excess[excess<0]
    if len(downside)==0: return 1
    return np.mean(excess)/np.std(downside) if np.std(downside)!=0 else 0
def max_drawdown(nav_series):
    if nav_series is None or len(nav_series)<2: return 0
    peak=nav_series[0]; max_dd=0
    for nav in nav_series:
        if nav>peak: peak=nav
        dd=(peak-nav)/peak if peak!=0 else 0
        if dd>max_dd: max_dd=dd
    return max_dd
