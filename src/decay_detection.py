
from src.engines.momentum import slope_and_r2
def detect_momentum_deceleration(nav_series, theta1=-0.5):
    if nav_series is None or len(nav_series)<7: return False, 0
    slope_1m, _ = slope_and_r2(nav_series[-1:])
    slope_6m, _ = slope_and_r2(nav_series[-6:])
    return (slope_1m - slope_6m) < theta1, slope_1m - slope_6m
def decay_penalty(is_decay): return 0.85 if is_decay else 1.0
def decay_flag(is_decay): return "🚩" if is_decay else "תקין"
