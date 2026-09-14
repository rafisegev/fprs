
import numpy as np
def excess_return(fund_return, bench_return):
    if fund_return is None or bench_return is None: return 0
    return fund_return - bench_return
def tracking_error(fund_returns, bench_returns):
    if fund_returns is None or bench_returns is None: return 0
    return np.std(np.array(fund_returns)-np.array(bench_returns))
