
# --- 🌿 ROOT QUANT REPORT ENGINE 🌿 ---
# ✅ Essa Testing Edition — Final ROOT in Progress
# Built for Essa — Junior Quant Analyst

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from datetime import datetime
import os, random
from colorama import Fore, Style, init
init(autoreset=True)

def cumulative_return(returns):
    return (1 + returns).cumprod() - 1

def geometric_annualized_return(returns, periods_per_year=252):
    compounded_growth = (1 + returns).prod()
    n_periods = returns.shape[0]
    return compounded_growth ** (periods_per_year / n_periods) - 1

def sharpe_ratio(returns, rfr):
    excess = returns - rfr / 252
    return np.sqrt(252) * excess.mean() / excess.std()

def sortino_ratio(returns, rfr):
    downside = returns[returns < 0]
    return np.sqrt(252) * (returns.mean() - rfr / 252) / downside.std()

def max_drawdown(returns):
    cum = (1 + returns).cumprod()
    peak = cum.cummax()
    return ((cum - peak) / peak).min()

def calculate_beta(port, market):
    aligned = port.align(market, join='inner')
    slope, _, _, _, _ = linregress(aligned[1], aligned[0])
    return slope

def run_root():
    print(Fore.GREEN + Style.BRIGHT + "\n🌿 Welcome to ROOT Preview Edition 🌿")

    start_date = input("Start Date (YYYY-MM-DD): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    risk_free_rate = float(input("Enter risk-free rate (e.g. 0.03 for 3%): "))

    mode = input("Portfolio mode? (manual/auto): ").lower()

    if mode == 'manual':
        tickers = input("Enter tickers (comma separated): ").upper().split(",")
        weights = {}
        print("Enter weights (total = 100):")
        for t in tickers:
            w = float(input(f"Weight for {t.strip()}: "))
            weights[t.strip()] = w / 100
    else:
        profile = input("Risk Profile? (low/medium/high): ").lower()
        horizon = input("Investment Horizon? (short/medium/long): ").lower()
        all_assets = {
            "low": ["IEF", "LQD", "SHY", "GLD"],
            "medium": ["SPY", "VEA", "VNQ", "DBC"],
            "high": ["VTI", "VWO", "QQQ", "ARKK"]
        }
        if profile not in all_assets:
            profile = "medium"
        assets = all_assets[profile]
        weights = {a: 1/len(assets) for a in assets}
        tickers = list(weights.keys())
        print(Fore.YELLOW + f"Auto Portfolio: {tickers} with equal weights")

    if "SPY" not in tickers:
        tickers.append("SPY")

    print(Fore.BLUE + "📥 Fetching data...")
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    prices = data["Adj Close"].dropna()

    returns = prices.pct_change().dropna()
    weights_series = pd.Series(weights)
    portfolio_returns = returns[tickers].mul(weights_series, axis=1).sum(axis=1)
    spy_returns = returns["SPY"]

    ann_return = geometric_annualized_return(portfolio_returns)
    sharpe = sharpe_ratio(portfolio_returns, risk_free_rate)
    sortino = sortino_ratio(portfolio_returns, risk_free_rate)
    mdd = max_drawdown(portfolio_returns)
    beta = calculate_beta(portfolio_returns, spy_returns)
    spy_cum = cumulative_return(spy_returns).iloc[-1]
    port_cum = cumulative_return(portfolio_returns).iloc[-1]

    results = {
        "Annualized Return": f"{ann_return:.2%}",
        "Cumulative Return": f"{port_cum:.2%}",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Sortino Ratio": f"{sortino:.2f}",
        "Max Drawdown": f"{mdd:.2%}",
        "Beta to SPY": f"{beta:.2f}",
        "SPY Cumulative": f"{spy_cum:.2%}"
    }

    os.makedirs("reports", exist_ok=True)
    df = pd.DataFrame(list(results.items()), columns=["Metric", "Value"])
    df.to_csv("reports/ROOT_Report_Data.csv", index=False)

    print(Fore.GREEN + "\n✅ Results saved to reports/ROOT_Report_Data.csv")

if __name__ == "__main__":
    run_root()
