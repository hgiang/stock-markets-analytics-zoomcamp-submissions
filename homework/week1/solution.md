# Module 1 homework — answers

Calculated on 26 August 2026. The data providers are live, so re-running the
script can produce revised values.

## Q1 — S&P 500 additions

**2025** had the largest number of additions among completed years from 2020:
**18**. The yearly counts were 2020: 10, 2021: 10, 2022: 15, 2023: 15,
2024: 16, and 2025: 18. (2026 was incomplete at the calculation date.)

**Additional:** 224 current S&P 500 constituents had been in the index for
more than 20 years.

Source: the first table of the Wikipedia S&P 500 companies page, using its
`Symbol`, `Security`, and `Date added` columns.

## Q2 — international indexes

Using the first and last available closes from 1 January through 21 August
2026, **2 of the 10 non-US indexes** outperformed the S&P 500. They were Japan
(+27.36%) and Canada (+14.86%), versus the S&P 500 (+11.90%).

| Index | YTD return |
|---|---:|
| Japan (Nikkei 225) | 27.36% |
| Canada (S&P/TSX Composite) | 14.86% |
| United States (S&P 500) | 11.90% |
| United Kingdom (FTSE 100) | 8.70% |
| Brazil (Ibovespa) | 6.54% |
| Germany (DAX) | 6.51% |
| Australia (S&P/ASX 200) | 3.79% |
| Mexico (IPC Mexico) | 2.48% |
| Hong Kong (Hang Seng) | -1.25% |
| China (Shanghai Composite) | -2.94% |
| India (Nifty 50) | -7.25% |

**Additional:** measured over exact 3-, 5-, and 10-year lookbacks ending on
21 August 2026, the counts outperforming the US were **2, 2, and 1**,
respectively. Thus, this sample does not show broad, persistent international
outperformance; it is concentrated in a small number of markets.

## Q3 — S&P 500 corrections

The median drawdown for corrections of at least 5% was **7.99%**.

| Percentile | Drawdown | Peak-to-trough duration |
|---|---:|---:|
| 25th | 6.23% | 22.00 days |
| 50th (median) | 7.99% | 40.50 days |
| 75th | 14.02% | 86.25 days |

I used strict record closing prices as all-time highs, found the minimum close
before each next record high, and calculated calendar-day peak-to-trough
duration. The top ten results match the assignment's supplied cross-check
(including 2007–09 at 56.8% and 517 days).

## Q4 — Amazon earnings surprises

For the 24 reported rows in the assignment's 25-row earnings-date sample
(beginning 2020-10-29), there were 20 positive surprises. The median 2-day
return was **+0.35%**. The Pearson correlation of surprise magnitude and the
2-day return was **+0.2217**.

This is weakly positive: a larger upside surprise was associated with a higher
short-horizon return in this small sample, but it is far too weak to treat as a
reliable standalone prediction signal. The calculation maps the announcement
to its next available trading session and uses `Close[t+1] / Close[t-1] - 1`.

## Q5 — proposed capstone

I want to predict which large US technology stocks will outperform the tech
market during the following month. I will use stocks such as Apple, Microsoft,
Nvidia, Amazon, Alphabet, and Meta. My model will use price momentum, RSI,
volatility, trading volume, and earnings surprises. I will compare its results
with buying the QQQ technology ETF.

## Q6 — useful additional metrics

- **Stock prices and volume:** download daily technology-stock data with
  yfinance to calculate momentum, RSI, and volatility.
- **QQQ and S&P 500:** download `QQQ` and `^GSPC` to compare each stock with
  the wider market.
- **VIX:** download `^VIX`; it measures market uncertainty.
- **Earnings surprises:** use `yf.Ticker(symbol).get_earnings_dates()` because
  earnings results can affect stock prices.

## Reproducing the calculation

Run [`homework1_solution.py`](homework1_solution.py) from the repository root:

```bash
uv run --with yfinance --with pandas --with lxml --with html5lib --with beautifulsoup4 \
  python homework/2026/week1/homework1_solution.py
```

`yfinance` treats `end` as exclusive, so the script uses `2026-08-22` as the
end bound to include the requested 21 August close.
