"""Reproducible calculations for Module 1 homework (2026 cohort).

Run from the repository root:
  uv run --with yfinance --with pandas --with lxml --with html5lib --with beautifulsoup4 \
    python homework/week1/homework1_solution.py

Data are live.  The printed values can change as Wikipedia/Yahoo Finance revise
their histories, and Q3 intentionally excludes the still-unfinished correction.
"""

from __future__ import annotations

from io import StringIO
import requests
import pandas as pd
import yfinance as yf


WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
INDEXES = {
    "United States (S&P 500)": "^GSPC",
    "China (Shanghai Composite)": "000001.SS",
    "Hong Kong (Hang Seng)": "^HSI",
    "Australia (S&P/ASX 200)": "^AXJO",
    "India (Nifty 50)": "^NSEI",
    "Canada (S&P/TSX Composite)": "^GSPTSE",
    "Germany (DAX)": "^GDAXI",
    "United Kingdom (FTSE 100)": "^FTSE",
    "Japan (Nikkei 225)": "^N225",
    "Mexico (IPC Mexico)": "^MXX",
    "Brazil (Ibovespa)": "^BVSP",
}


def close_history(symbol: str, start: str, end: str | None = None) -> pd.Series:
    """Return a named, timezone-naive Close series; ``end`` is Yahoo-exclusive."""
    frame = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=False)
    if frame.empty:
        raise RuntimeError(f"No Yahoo Finance data returned for {symbol}")
    series = frame["Close"].copy()
    series.index = pd.to_datetime(series.index).tz_localize(None)
    return series


def question_1() -> None:
    response = requests.get(WIKI_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    constituents = pd.read_html(StringIO(response.text))[0]
    additions = constituents[["Symbol", "Security", "Date added"]].copy()
    additions["year_added"] = pd.to_datetime(additions["Date added"], errors="coerce").dt.year
    counts = additions[additions.year_added.ge(2020)].groupby("year_added").size()
    old_members = (pd.Timestamp.today().normalize() - pd.to_datetime(additions["Date added"])).dt.days.gt(20 * 365.25).sum()
    print("Q1 additions by year (2020+):\n", counts)
    print("Q1 answer:", int(counts.idxmax()), "with", int(counts.max()), "additions")
    print("Q1 additional — current constituents added >20 years ago:", int(old_members))


def question_2() -> None:
    # 2026-08-22 is deliberate: yfinance's end parameter is exclusive, so this
    # includes the requested 21 August close.
    ytd = {}
    for name, symbol in INDEXES.items():
        close = close_history(symbol, "2026-01-01", "2026-08-22")
        ytd[name] = close.iloc[-1] / close.iloc[0] - 1
    returns = pd.Series(ytd, name="YTD return").sort_values(ascending=False)
    us_return = returns["United States (S&P 500)"]
    print("\nQ2 YTD returns through 2026-08-21:\n", (returns * 100).round(2))
    print("Q2 answer — better than the US:", int((returns.drop("United States (S&P 500)") > us_return).sum()), "of 10")

    # Use the last available close on/before 21 Aug for every respective lookback.
    end = pd.Timestamp("2026-08-22")
    for years in (3, 5, 10):
        period_returns = {}
        for name, symbol in INDEXES.items():
            close = close_history(symbol, f"{2026 - years}-08-21", end.strftime("%Y-%m-%d"))
            period_returns[name] = close.iloc[-1] / close.iloc[0] - 1
        period_returns = pd.Series(period_returns)
        better = (period_returns.drop("United States (S&P 500)") > period_returns["United States (S&P 500)"]).sum()
        print(f"Q2 additional — {years}-year return leaders vs US: {better} of 10")


def question_3() -> None:
    close = close_history("^GSPC", "1950-01-01")
    # A strict record close is an all-time-high point; pairing each record with
    # the next follows the homework definition exactly.
    ath = close[close > close.cummax().shift(1)]
    corrections: list[dict[str, object]] = []
    for high_date, next_high_date in zip(ath.index[:-1], ath.index[1:]):
        trough = close.loc[high_date:next_high_date].iloc[:-1]
        low_date, low = trough.idxmin(), trough.min()
        high = close.loc[high_date]
        drawdown = (high - low) / high * 100
        if drawdown >= 5:
            corrections.append({"peak": high_date, "trough": low_date, "drawdown_pct": drawdown,
                                "duration_days": (low_date - high_date).days})
    result = pd.DataFrame(corrections)
    print("\nQ3 correction percentiles (25%, median, 75%):")
    print(result[["drawdown_pct", "duration_days"]].quantile([.25, .50, .75]).round(2))
    print("Q3 median drawdown (%):", round(result.drawdown_pct.median(), 2))
    print("Q3 top 10 drawdowns:\n", result.nlargest(10, "drawdown_pct").to_string(index=False))


def question_4() -> None:
    amzn = yf.Ticker("AMZN")
    # The assignment's requested sample is 25 rows (one future event plus the
    # 24 reported events beginning 2020-10-29).
    earnings = amzn.get_earnings_dates(limit=25)
    earnings.index = pd.to_datetime(earnings.index).tz_localize(None).normalize()
    earnings = earnings.dropna(subset=["Reported EPS", "Surprise(%)"])
    prices = close_history("AMZN", "2020-01-01")
    # Map any calendar announcement date to its next trading session, then
    # calculate Close[t+1]/Close[t-1]-1 (the three consecutive trading days).
    rows = []
    for announced, row in earnings.iterrows():
        position = prices.index.searchsorted(announced)
        if position == len(prices) or position == 0 or position + 1 >= len(prices):
            continue
        two_day_return = prices.iloc[position + 1] / prices.iloc[position - 1] - 1
        rows.append({"announcement": announced, "surprise_pct": row["Surprise(%)"], "two_day_return": two_day_return})
    result = pd.DataFrame(rows)
    positive = result[result.surprise_pct > 0]
    print("\nQ4 observations used:", len(result), "; positive surprises:", len(positive))
    print("Q4 answer — median 2-day return after positive surprises (%):", round(positive.two_day_return.median() * 100, 2))
    print("Q4 correlation (surprise % vs 2-day return):", round(result[["surprise_pct", "two_day_return"]].corr().iloc[0, 1], 4))
    print(result.to_string(index=False))


if __name__ == "__main__":
    question_1()
    question_2()
    question_3()
    question_4()
