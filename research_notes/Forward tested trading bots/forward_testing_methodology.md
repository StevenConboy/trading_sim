# Forward-Testing a Trading Bot on Alpaca Paper: Realism, Statistics, Professional Practice, and the trading_sim Repo

Notes compiled 2026-11-23. Numbers marked "computed" come from Python (`statistics.NormalDist`) using the cited formulas. Where possible, each computation was first checked against a number the source paper prints itself. Where a fact comes only from a search-engine snippet and not from a page I fetched, it is flagged "(snippet, not fetched)".

---

## 1. How realistic is Alpaca paper trading, and what does it not simulate?

### Takeaway
Alpaca paper trading fills each order against the current NBBO quote. It does not model market impact, queue position, latency slippage, price improvement, regulatory fees or dividends, and it adds random partial fills on purpose. So it tests code and order handling, not execution quality. On the free plan, options add a second problem. The "indicative" options feed the bot sees is a derived, adjusted approximation of OPRA, which Alpaca staff call "not real data", and Alpaca does not document which quotes its paper engine uses to fill options. The pattern day trader (PDT) rule no longer exists at Alpaca: FINRA retired it effective June 4, 2026.

### Cited Findings

#### How paper fills work (official documentation)
- Paper trading "simulates the order filling based on the real-time quotes", and orders "will be matched against the best available current market price (NBBO)". — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- "A non-marketable buy limit order will not be filled until its limit price is equal to or greater than the best ask price" (sell limits work the same way against the bid). — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- "Your order quantity is not checked against the NBBO quantities", so there is no check on depth or liquidity. — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- Orders "will receive partial fills for a random size 10% of the time". If the order is still marketable, the rest is re-evaluated for a later fill. — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- The "Paper vs Live" list of things paper does NOT simulate: "Market impact of your orders", "Information leakage of your orders", "Price slippage due to latency", "Order queue position (for non-marketable limit orders)", "Price improvement received", "Regulatory fees", "Dividends". The comparison table marks "Borrow Fees" as "⛔️ (Coming Soon!)" for paper. — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- The default paper balance is "$100k", and it can be reset to any amount. Paper accounts do not send fill emails. "The API spec is the same between the paper trading and live accounts." "Anyone globally can create an Alpaca Paper Only Account!" — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- On Dec 9, 2025 a user reported 49–259 s "delays" on small-cap limit orders. Alpaca staff (Dan_Whitnable_Alpaca) replied: "There is no delay or batching". Fills use real-time NBBO, and the orders filled "when the ask price was at or below your limit price". Also: "The paper trading simulator randomly creates partial fills to ensure the algo handles these partials gracefully." Per staff, the simulator ignores volatility and liquidity. — [Alpaca Forum: Paper Trading Fill Delays of 50–260 Seconds](https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223)

#### Options-specific realism reports (community, mixed reliability)
- In April 2025 a user reported that more than half of their paper SPY option limit orders (March 2025) filled at or better than the limit: buys below the limit, sells above it. One reply (author's role not labeled) said: "This is happening due to price improvement and can happen in live trading as well." Another user said paper options trading "will never get close to actual liquidity and fills" except in very liquid products (SPY, SPX, QQQ) with market orders. — [Alpaca Forum: Paper account options limit orders](https://forum.alpaca.markets/t/paper-account-options-limit-orders/16652). **Conflict:** the official docs list "Price improvement received" as NOT simulated in paper. — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- Alpaca staff, Sep 12, 2025: data does not depend on account type, so paper and live get the same data. On the Basic plan, latest option quotes come from the `indicative` feed, which is "not real data and should not be used for live trading". Staff, Feb 1, 2026: indicative "can vary from the actual `opra` data", and missing bids or asks are common for thinly traded options. **No staff reply in the thread says which quotes the paper simulator uses to fill options orders.** — [Alpaca Forum: Paper Trading Options Pricing](https://forum.alpaca.markets/t/paper-trading-options-pricing/17795)
- In the same thread, a user reported a strategy win rate of 45% on live data against 82% on 15-minute-delayed data. He concluded that paper chain data was delayed; staff did not confirm this. — [Alpaca Forum: Paper Trading Options Pricing](https://forum.alpaca.markets/t/paper-trading-options-pricing/17795)

#### Market data: IEX vs SIP, indicative vs OPRA
- The Basic (free) plan is "the default option for both Paper and Live trading accounts". For equities it gives real-time data from "only the IEX exchange", restricts historical data from the "latest 15 minutes", and allows 30 WebSocket symbols and 200 historical calls/min. For options it gives the "Indicative Pricing Feed" (200 WebSocket quotes). Algo Trader Plus costs **$99/month** and gives "All US Stock Exchanges" for equities, the "OPRA Feed" for options, no historical restriction, and 10,000 calls/min. — [Alpaca Docs: About Market Data API](https://docs.alpaca.markets/docs/about-market-data-api)
- "Indicative Pricing Feed is a free derivative of the original OPRA feed: the quotes are not actual OPRA quotes, they're just indicative derivatives. The trades are also derivatives and they're delayed by 15 minutes." "OPRA feed is only available to subscribed users." "Currently we only offer historical option data since February 2024." — [Alpaca Docs: Historical Option Data](https://docs.alpaca.markets/docs/historical-option-data)
- (Snippet, not fetched) Per search snippets, staff wrote that indicative option quotes "are not delayed, but adjusted" and that the feed is sampled at no more than one quote per second. An Alpaca status incident once reported outdated indicative bid/ask prices for some symbols. — [Alpaca Forum: What is the Indicative Pricing Feed for options?](https://forum.alpaca.markets/t/what-is-the-indicative-pricing-feed-for-options/14595); [Alpaca Forum: Options price update frequency](https://forum.alpaca.markets/t/options-price-update-frequency/18082); [Alpaca Status incident](https://status.alpaca.markets/incidents/nndsynn3ztwv)

#### Options and 0DTE mechanics relevant to a paper test
- "In the Paper environment, options trading capability will be enabled by default". Option orders must have a whole-number `qty`, no `notional`, `time_in_force` of `day` or `gtc`, and no extended hours. Allowed order types are market, limit, stop and stop_limit. "On PAPER NTAs [non-trade activities such as exercises and expirations] are synced at the start of the following day." Alpaca "will automatically exercise in-the-money (ITM) contracts at expiry" if they are ITM by at least $0.01, and may "sell-out the position within 1 hour before expiry" when buying power is insufficient. — [Alpaca Docs: Options Trading](https://docs.alpaca.markets/docs/options-trading)
- The 0DTE FAQ (page updated 2026-11-13) gives these rules:
  - Opening-order cutoffs are 3:15 PM ET for stocks and most equity options and 3:30 PM ET for broad-based ETFs. "SPXW/XSP 0DTE stop trading at 4:00 PM ET on expiration day."
  - Auto-liquidation typically starts at 3:30 PM ET for equity options and 3:45 PM ET for broad ETFs. It targets near-the-money positions (about 0.5% from the underlying) that the account cannot support. "Far OTM longs are not liquidated for possible after-close moves."
  - Alpaca cancels opening orders on contracts expiring that day; closing orders can keep working.
  - Index options are "European-style and cash-settled (no shares)" and "generally fall outside equity American-style sellout logic". Enabling index options requires contacting Alpaca.
  - The page says nothing about paper accounts.

  — [Alpaca Docs: Options Expiration & 0 DTE FAQ](https://docs.alpaca.markets/us/docs/options-expiration-0-dte-faq)

#### PDT rule (changed in 2026)
- The SEC approved FINRA's SR-FINRA-2025-017 on April 14, 2026. It removes the "pattern day trader" definition and the $25,000 minimum equity requirement from FINRA Rule 4210 and replaces them with an intraday margin standard. It took effect **June 4, 2026**, with a phase-in period ending October 20, 2027 (snippet-level detail; the notice PDF was not fetched). — [FINRA Regulatory Notice 26-10](https://www.finra.org/sites/default/files/2026-04/Regulatory-Notice-26-10.pdf); [WilmerHale client alert (2026-04-23)](https://wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard)
- Alpaca says the PDT designation, all PDT-based restrictions and the $25k minimum are gone as of June 4, 2026, replaced by an intraday margin framework. Its PDT and day-trading-buying-power API fields (`pattern_day_trader`, `daytrade_count`, etc.) were deprecated, with removal set for 2026-07-06. Reg T requirements still apply (snippet, not fetched). — [Alpaca blog: FINRA Retires the PDT Rule](https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/); [Alpaca changelog 2026-06-03](https://docs.alpaca.markets/us/changelog/2026-06-03-pdt-651df23); [Alpaca Docs: The Intraday Margin Rule](https://docs.alpaca.markets/docs/the-intraday-margin-rule)
- Alpaca's User Protection page (updated 2026-09-16) now lists the "Intraday Margin Rule". It says "Our wash trade protection also applies to your paper trading account", and wash trades are rejected with HTTP 403. Margin protections "do not apply to crypto trading as cryptocurrencies are not marginable." — [Alpaca Docs: User Protection](https://docs.alpaca.markets/docs/user-protection)

#### Crypto paper trading
- "Paper trading simulates crypto trading as well." — [Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)
- Live crypto fees are tiered by 30-day volume. Tier 1 ($0–100k) is 15 bps maker / 25 bps taker, falling to 0 / 10 bps above $100M. Supported orders are market, limit and stop limit, with `gtc` or `ioc`, 24/7. Crypto "cannot be bought on margin" and "can not be sold short". The exchange field is "ALPACA". **The page does not say whether fees are charged in paper.** — [Alpaca Docs: Crypto Trading](https://docs.alpaca.markets/docs/crypto-trading)

### Inferences
- Paper P&L is an **optimistic bound** for anything that depends on the size of the bid-ask spread, liquidity, or resting limit orders. A resting limit can fill as soon as the NBBO touches it, with no queue. That is weakest for cheap, wide-spread, deep-OTM 0DTE options, which is exactly what trading_sim trades.
- The documented rule ("matched against ... NBBO", no queue position) means a resting sell limit can be booked at the *current bid* when the market jumps through the limit price. In a live market the order would rest on the book and normally fill at its own limit. Fills "better than the limit" are therefore more likely a simulator artifact than real price improvement. This is my inference; it is consistent with the docs and with forum thread 16652, but Alpaca has not confirmed it.
- If a bot prices its orders off indicative quotes while the paper engine fills against something else (possibly real OPRA NBBO, which is undocumented), its limits may be mis-placed. Symptoms would be "limit at the bid did not fill" or "no quote" rejections. Logging both the quote used and the fill is essential.
- Paper does not deduct regulatory fees, and live costs on options are per contract. A forward test should therefore subtract an estimated live cost per contract after the fact. That matters most when the premium is about $8–$10 per contract.
- Since June 4, 2026, PDT is not a binding constraint on a small account doing several round-trips a day. Earlier tutorials that warn about it are out of date.
- Wash-trade protection applies in paper. Two "arms" trading the same contract could be rejected (403) if one arm's buy limit is at or above the other arm's resting sell limit.

### Gaps
- Alpaca does not document which quote stream (real OPRA NBBO or indicative) its paper engine uses to fill **options** orders for free-plan accounts. I found no staff answer.
- I could not confirm whether the 3:30/3:45 PM auto-liquidation, the auto-exercise of ITM options, and the sell-out logic run in **paper** accounts. The FAQ does not mention paper.
- Whether paper simulates crypto fees, short-borrow and hard-to-borrow rules, or corporate actions other than dividends (splits, etc.) is not documented. A search snippet suggested splits are also not simulated, but I could not tie it to a fetched page.
- I did not verify Alpaca's live per-contract fee schedule for options or index options (regulatory pass-through fees, any index-option fees).
- I found no Alpaca source giving IEX's share of consolidated volume.
- PDT details are from search summaries of the Alpaca blog, changelog and FINRA notice; I did not fetch those pages directly. I did not confirm how the new intraday margin framework behaves in paper accounts.

---

## 2. How long must a forward test run to mean anything?

### Takeaway
A Sharpe ratio estimated from one year of daily returns has a standard error of about 1.0 (annualized), so a year of paper trading cannot tell Sharpe 0 from Sharpe 1. Confirming at 95% (one-sided) that Sharpe > 0 takes about **10.8 years** of daily data for a true Sharpe of 0.5, **2.7 years** for 1.0, and **8 months** for 2.0, if returns are normal. Even then the chance of passing is only 50%; 80% power roughly doubles those times. Fat tails, few trades per year, and picking the best of several bots all push the requirement much higher. If 10 skill-free paper bots run for a year, the best is expected to show an annualized Sharpe of about **1.6**.

### Cited Findings

#### Lo (2002), "The Statistics of Sharpe Ratios", Financial Analysts Journal 58(4):36–52
- For IID returns, the asymptotic variance is V_IID = 1 + SR²/2 (Eq. 8). The standard error is **SE(SR̂) ≈ sqrt((1 + SR²/2) / T)** (Eq. 9), and the 95% confidence interval is **SR̂ ± 1.96 · sqrt((1 + SR̂²/2) / T)** (Eq. 10). SR and T are in the same period units. — [Lo (2002), PDF](https://traders.studentorg.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf); [CFA Institute listing](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios)
- "In a sample of 60 observations, the standard error of the Sharpe ratio estimator is 0.188 when the true Sharpe ratio is 1.50 but is 0.303 when the true Sharpe ratio is 3.00." Table 1, row SR = 0.50: SE = 0.306 (T=12), 0.217 (24), 0.177 (36), 0.153 (48), 0.137 (60), 0.095 (125), 0.067 (250), 0.047 (500). — [Lo (2002)](https://traders.studentorg.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf)
- The annual "Sharpe ratio for a hedge fund can be overstated by as much as 65 percent because of the presence of serial correlation in monthly returns". Naive sqrt(q) annualization is wrong when returns are autocorrelated. — [Lo (2002)](https://traders.studentorg.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf)

#### Bailey & López de Prado (2012), "The Sharpe Ratio Efficient Frontier", Journal of Risk: PSR and MinTRL
- Formulas: the PDF's math glyphs did not extract, so I reconstructed them in this standard form and checked them by reproducing the paper's 2.73 / 2.83 / 3.24-year examples to three digits (computed).
  - **PSR(SR\*) = Φ[ (SR̂ − SR\*) · sqrt(n − 1) / sqrt(1 − γ₃·SR̂ + ((γ₄ − 1)/4)·SR̂²) ]**
  - **MinTRL = 1 + [1 − γ₃·SR̂ + ((γ₄ − 1)/4)·SR̂²] · (Z_α / (SR̂ − SR\*))²**
  - γ₃ is skewness and γ₄ is kurtosis (3 for a normal distribution). SR̂ and SR\* "are expressed in the same frequency as the returns time series".

  — [Bailey & López de Prado (2012), PDF](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf)
- "MinTRL is expressed in terms of number of observations, not annual or calendar terms." The result rests on the central limit theorem, which "is typically assumed to hold for samples in excess of 30 observations". The skew and kurtosis inputs "must be computed on longer series for CLT to hold". — [Bailey & López de Prado (2012)](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf)
- Worked examples from the paper, all at 95% confidence:
  - For daily IID normal returns, "a 2.73 years track record is required for an annualized Sharpe of 2 to be considered greater than 1".
  - With weekly returns it is 2.83 years (+3.7%); with monthly returns, 3.24 years (+18.7%).
  - With the HFR hedge fund index's skew and kurtosis (monthly), it is 4.99 years: "54% longer" than normal monthly and "82.8% longer" than normal daily.

  — [Bailey & López de Prado (2012)](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf)
- PSR example: an annualized Sharpe of 1.59 over 2 years of monthly data passes the skill-less benchmark when normality is assumed, but fails at 95% once its negative skew and fat tails are included. With 3 years of data it would pass. Of HFR style indices from 2000–2011 (134 months), "only 9 style indices substantiate investment skill over an annualized Sharpe ratio of 0.5 at a 95% confidence level". — [Bailey & López de Prado (2012)](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf)

#### Deflated Sharpe Ratio: selection bias across many trials (Bailey & López de Prado 2014, Journal of Portfolio Management)
- Expected maximum Sharpe ratio after N independent trials when the true Sharpe is zero: **E[max SR̂ₙ] ≈ sqrt(V[{SR̂ₙ}]) · ((1 − γ)·Φ⁻¹[1 − 1/N] + γ·Φ⁻¹[1 − 1/(N·e)])**. Here γ "(approx. 0.5772) is the Euler-Mascheroni constant", Φ is the standard normal CDF, and e is Euler's number. — [Bailey & López de Prado (2014), PDF](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- "Essentially, DSR is a PSR where the rejection threshold is adjusted to reflect the multiplicity of trials." The expected maximum "increases as more independent trials are attempted (N), or the trials involve a greater variance". — [Bailey & López de Prado (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- Worked example: a strategist's best Treasury-auction configuration shows an annualized Sharpe of 2.5 over 5 years of daily data (T = 1250). The investor asks for "i) The number of independent trials carried out (N); ii) the variance of the backtest results; iii) the sample length (T); and iv) the skewness and kurtosis". The investor concludes there is "only a 90% chance that the true SR ... is greater than zero" and declines. With N = 46 trials, DSR "would have been 0.9505". — [Bailey & López de Prado (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf). The input values did not extract from the PDF. N = 100, V[SR] = 0.5 (annualized), skew = −3 and kurtosis = 10 reproduce both printed outputs exactly: DSR = 0.9004 and 0.9505 (computed).
- The paper compares the practice of hiding failed trials to the problem addressed by the AllTrials movement in medicine, "which would require the results of all trials to be made public". — [Bailey & López de Prado (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)

#### Multiple-testing haircuts and backtest length
- Harvey & Liu: "A common practice in evaluating backtests of trading strategies is to discount the reported Sharpe ratios by 50%." "The 50% haircut is only a rule of thumb." "We argue that it is a serious mistake to use the usual 50% haircut. Our results show that the multiple testing haircut is nonlinear. The highest Sharpe ratios are only moderately penalized, while the marginal Sharpe ratios are heavily penalized." Their example: with at least 316 factors tested (Harvey, Liu, Zhu), a t-ratio of 3.0 becomes an adjusted 2.0. They use Bonferroni, Holm and BHY adjustments. SR = t-ratio / sqrt(T). Caveat: high Sharpe ratios can come from "an option-like strategy with high ex ante negative skew". — [Harvey & Liu (2015), "Backtesting", JPM](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
- (Snippet, not fetched) A 2017 Bailey slide deck: "If only 2 years of daily backtest data are available, then no more than 7 strategy variations should be tried"; for 5 years, "no more than 45". — [Bailey, 2017 slides (Berkeley CDAR)](https://cdar.berkeley.edu/sites/default/files/dhb-risk-2017.pdf). I could not fetch the original paper ([Notices of the AMS, 2014](https://www.ams.org/notices/201405/rnoti-p458.pdf), HTTP 403).
- (Snippet, not fetched) "A Sharpe ratio of 0.5 ... we'd have to hold them for 16 years to be 95% confident that our realized excess return is positive." — [IFA: How Long Is Long Enough](https://www.ifa.com/articles/long_long_enough_-_most_hands_dont_clear_skill). This is consistent with the 15.4 years computed below.

### Inferences

**A. Lo standard error for a true annualized Sharpe of 1.0, from daily data (computed with Eq. 9, n = 252·years):** the rule of thumb is SE(annualized SR) ≈ 1/sqrt(years), almost regardless of sampling frequency.

| Track record | SE (annualized) | 95% CI if observed SR = 1.0 |
|---|---|---|
| 3 months | 2.00 | −2.92 to +4.92 |
| 6 months | 1.42 | −1.77 to +3.77 |
| 1 year | 1.00 | −0.96 to +2.96 |
| 2 years | 0.71 | −0.39 to +2.39 |
| 3 years | 0.58 | −0.13 to +2.13 |
| 5 years | 0.45 | +0.12 to +1.88 |
| 10 years | 0.32 | +0.38 to +1.62 |

**B. MinTRL to be 95% confident that SR > 0 (computed; daily IID normal, q = 252):**

| Annualized SR | One-sided 95% | Two-sided 95% (one-sided 97.5%) | ≈80% power (n ≈ (1+SR²/2)·((1.645+0.842)/SR)²) |
|---|---|---|---|
| 0.5 | 2,730 days ≈ **10.8 yrs** | 3,875 days ≈ 15.4 yrs | ≈ 24.7 yrs |
| 1.0 | 684 days ≈ **2.7 yrs** | 971 days ≈ 3.9 yrs | ≈ 6.2 yrs |
| 1.5 | 305 days ≈ 1.2 yrs | 433 days ≈ 1.7 yrs | — |
| 2.0 | 173 days ≈ **0.69 yrs (~8 months)** | 245 days ≈ 0.97 yrs | ≈ 1.6 yrs |
| 3.0 | 78 days ≈ 0.31 yrs | 110 days ≈ 0.44 yrs | ≈ 0.7 yrs |

- With monthly observations: SR 0.5 needs 132 months (11.0 yrs), SR 1.0 needs 35 months (2.9 yrs), and SR 2.0 needs 10 months. Ten points is below the paper's 30-observation CLT floor, so it is not trustworthy.
- MinTRL plugs in the *observed* SR. If the true SR equals the MinTRL input, a test run exactly that long passes only about 50% of the time. The 80% power column is the honest planning number. This is my reading of the formula's construction.

**C. Selection bias from running several paper bots and keeping the best.** Expected best annualized Sharpe among N independent strategies with true Sharpe 0 (computed with the DSR formula and V[SR_annual] ≈ 1/years):

| Forward-test length | N=2 | N=5 | N=10 | N=20 | N=50 | N=100 |
|---|---|---|---|---|---|---|
| 3 months | 1.04 | 2.39 | 3.15 | 3.80 | 4.55 | 5.06 |
| 6 months | 0.74 | 1.69 | 2.23 | 2.69 | 3.22 | 3.58 |
| 1 year | 0.52 | 1.19 | 1.57 | 1.90 | 2.28 | 2.53 |
| 2 years | 0.37 | 0.84 | 1.11 | 1.34 | 1.61 | 1.79 |

- Forward testing does not escape multiple testing. Running 10 prompt variants or 10 bots on paper for 6 months and promoting the winner is expected to produce a Sharpe of about 2.2 from pure luck. N must count every variant ever forward-tested and then dropped, not just the survivor.
- The same formula reproduces the slide-deck limits: E[max] = 1 needs about 1.92 years at N = 7 and about 5.0 years at N = 45 (computed). That is consistent with "7 variations / 2 years" and "45 / 5 years".

**D. Win-rate (directional accuracy) tests instead of Sharpe.** When each trade is a binary call (up or down), a binomial test against 50% is more direct. Sample sizes for one-sided α = 0.05 and 80% power (computed, normal approximation):

| True hit rate | Trades needed | At 1 trade/day |
|---|---|---|
| 52% | 3,863 | ≈ 15.3 yrs |
| 53% | 1,716 | ≈ 6.8 yrs |
| 55% | 617 | ≈ 2.4 yrs |
| 60% | 153 | ≈ 0.6 yrs |
| 65% | 67 | ≈ 0.3 yrs |

- Exact chance of doing at least this well by coin-flipping (computed): 4/4 = 6.3%; 14/20 = 5.8%; 38/60 = 2.6%; 59/100 = 4.4%; 140/250 = 3.3%. A 250-day test has 80% power only for a true accuracy of about 58% or more.

**E. Lottery-ticket payoffs (like buying $0.10 0DTE options).** Illustrative only: lose 100% with probability 1−p, gain +900% (10x) with probability p (computed with the MinTRL formula including skew and kurtosis):
- p = 0.10: zero edge.
- p = 0.11: +10% per trade, per-trade SR 0.032, skew 2.5, kurtosis 7.2. Needs about **2,443 trades (≈9.7 years at one a day)**.
- p = 0.12: +20% per trade. Needs about 616 trades (≈2.4 years).
- p = 0.15: +50% per trade. Needs about 104 trades.
- Even very large per-trade edges take years to establish at one trade per day. With such skewed data the CLT-based formulas are only rough guides; permutation or bootstrap tests are safer.

**F. Optional stopping.** Checking the P&L every day and declaring success the first time it looks significant inflates false positives. The sample size or stop date should be fixed in advance. This is standard statistical reasoning; I did not fetch a specific source for it.

### Gaps
- The exact published MinBTL formula and wording in Bailey, Borwein, López de Prado & Zhu (2014) could not be fetched (AMS returned 403). The "7 / 45 variations" figures come from a slide-deck snippet, cross-checked by my computation.
- The PSR and MinTRL formula text did not extract from the PDF (missing glyphs). The formulas above were reconstructed and checked numerically against three printed examples, not read directly.
- I did not fetch Lo's (2002) full non-IID (autocorrelation-adjusted) annualization formula, only the headline "65 percent" figure.

---

## 3. How do professionals incubate and verify strategies?

### Takeaway
Professionals treat a strategy as a sequence of gates. The backtest is followed by an embargo or out-of-sample period, then paper trading on a live feed, then a small allocation of real capital ("graduation"), then gradual scaling, and finally decommissioning. Rules are frozen during each stage, and kill criteria are set in advance. Investors judge a record by its length, all the trials that were tried, its skew and kurtosis, and costs, not by the headline Sharpe. Allocators typically ask for 3+ years of monthly returns. A home-made forward record becomes credible when the decisions are timestamped *before* the outcome by something the trader cannot edit: a third-party clock, the broker's own order records, or a public append-only log.

### Cited Findings

#### Staged lifecycle and incubation
- (Secondary summaries, snippet-level) López de Prado's strategy life cycle in *Advances in Financial Machine Learning* (2018, ch. 1) has five stages:
  - **Embargo**: run on data after the backtest end date, and advance only if performance matches the backtest.
  - **Paper trading**: run on a live real-time feed until there is enough evidence; this captures real latencies in parsing, calculation and execution.
  - **Graduation**: manage real capital, alone or in an ensemble, with risk, returns and costs measured.
  - **Re-allocation**: allocation starts small, grows with consistent performance, and shrinks as performance decays.
  - **Decommission**.

  — [AFML study notes (chenqijunvc.github.io)](https://chenqijunvc.github.io/Advance-in-Financial-Machine-Learning-Study-Notes); [The MLdP Pipeline (Substack)](https://tradeandroll.substack.com/p/the-mldp-pipeline-building-production). The study-notes page returned 404 when fetched. I could not verify the book's exact wording.
- Kevin Davey, in the host's paraphrase rather than a direct quote: after walk-forward and Monte Carlo testing, strategies are monitored "without real money" for "6 to 12 months". Incubation "exposes them to real-time dynamics like slippage, commissions, and data anomalies not fully captured in backtests". "85-90%" of surveyed students credited incubation with "avoiding bad strategies or confirming good ones". There is a monthly process of "removing poor performing strategies and substituting in better performing ones". — [Algo Advantage #036, Kevin Davey Part I](https://algoadvantage.substack.com/p/036-kevin-davey-part-i-its-all-about) (also at [IBKR Campus](https://www.interactivebrokers.com/campus/ibkr-quant-news/algo-advantage-036-kevin-davey-part-i-its-all-about-process-in-algo-trading/))
- (Snippet, not fetched) Other secondary sources give Davey's incubation as "six to nine months" ([Algo Advantage #037](https://algoadvantage.substack.com/p/037-kevin-davey-ii-selecting-optimal)), or 3–6 months and 4–12 weeks with no code edits ([forex.in.rs](https://www.forex.in.rs/simple-systems-diversified), low reliability). His book *Building Winning Algorithmic Trading Systems* has a chapter "Monte Carlo Testing and Incubation", whose text I did not see.

#### Evidence standards allocators apply
- It is "common practice in the hedge fund industry to ask for track records greater than 3 or more years of monthly returns." — [Bailey & López de Prado (2012)](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf)
- An informed investor asks for the number of independent trials, the variance of their Sharpe ratios, the sample length, and the skewness and kurtosis. A Sharpe of 2.5 over 5 years was rejected on those grounds. — [Bailey & López de Prado (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- Haircuts should be nonlinear in the number of tests. Strategies with marginal Sharpe ratios are heavily penalized. — [Harvey & Liu (2015)](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)

#### Making a forward record verifiable
- Git dates can be set by the author: `--date=<date>` will "Override the author date used in the commit", and "The `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` environment variables support the following date formats". `-S`/`--gpg-sign` "GPG-sign[s] commits". That proves *who*, not *when*. — [git-scm: git-commit](https://git-scm.com/docs/git-commit)
- OpenTimestamps git integration: git-ots "records evidence that selected Git commits existed before a Bitcoin block was mined". Verification needs only a Bitcoin block header. The project is early (v0.0.1) (snippet). Peter Todd's 2016 method timestamps PGP-signed commits and tags and is backwards compatible with ordinary git clients. — [git-ots (PyPI)](https://pypi.org/project/git-ots/); [Peter Todd: OpenTimestamps Git Integration](https://petertodd.org/2016/opentimestamps-git-integration)
- (Snippet, vendor source, low reliability) "Verification means a third party you can access directly (Myfxbook, Darwinex, a broker's own public page) reports the results, so the trader cannot edit history." — [MQL5 blog post](https://www.mql5.com/en/blogs/post/773638). A standard hypothetical-performance disclaimer: "no hypothetical trading record can completely account for the impact of financial risk in actual trading." — [NinjaTrader Follow disclosure](https://follow.ninjatrader.com/details/155882308)
- Alpaca's paper account sends no fill emails ([Alpaca Docs: Paper Trading](https://docs.alpaca.markets/docs/paper-trading)), and paper option non-trade activities sync the next day ([Alpaca Docs: Options Trading](https://docs.alpaca.markets/docs/options-trading)). The broker-side evidence for a paper record is therefore the API's order and activity history, not statements sent to the user.

### Inferences
Below is a practical protocol for a solo forward test, synthesized from the sources above.

1. **Pre-register before the first trade**, and commit and timestamp it. The document should state:
   - the hypothesis and the primary metric (one metric);
   - the statistical test and α;
   - the fixed sample size or stop date, from a power calculation as in Section 2;
   - the universe, entry, exit and sizing rules;
   - the data feed;
   - the live cost model (spread, fees);
   - kill criteria;
   - a running count of variants tried (N for DSR).
2. **Freeze the rules.** Tag a release, and stamp every trade row with the git commit hash of the code and rules it ran under. Bug fixes to execution are allowed but should be logged as dated amendments. If the signal logic changes, restart the clock.
3. **Commit the decision before the outcome**: direction, reason, and a hash of the data snapshot used. Push it to a third-party host and anchor it with OpenTimestamps. Afterwards, reconcile every row against the broker's own records (order IDs, `client_order_id`, server timestamps, fills, and option expirations and exercises).
4. **Book conservatively:**
   - entries at the ask and exits at the bid;
   - resting-limit exits at the limit price, never better;
   - estimated live fees subtracted;
   - unresolved positions marked to zero until reconciled.
5. **Benchmarks.** Use a randomized control with the same structure (trading_sim's coin arm is ideal), plus "do nothing". For stock strategies, also use SPY total return computed from data, because paper does not credit dividends. Report after-cost P&L, hit rate, Sharpe with a Lo CI, PSR(0), DSR with an honest N, max drawdown, and the number of trades.
6. **Gate to real money.**
   - Paper proves only the mechanics.
   - Move to the smallest live size only after the pre-registered test passes. That means one-sided p < 0.05 at the planned n, or PSR/DSR ≥ 0.95 with every trial counted.
   - Then compare live fills with paper fills for a fixed period, as a slippage calibration, before scaling.
   - Scale gradually, and decommission on pre-set criteria, for example a loss budget or a drawdown beyond X times the expected level.

### Gaps
- My searches did not reach Robert Carver's blog or books, Ernest Chan's paper-trading guidance, or QuantStart and Quantocracy material. No Carver-specific views are reported here.
- I found no primary source (firm documentation) describing how specific prop firms or CTAs run incubation. Only secondary summaries of López de Prado and Davey were found.
- I did not research GIPS verification standards, or whether GitHub push-event timestamps are retained and publicly verifiable.
- I found no third-party performance tracker with a documented Alpaca integration. Vendor "verified" claims in the search results were marketing, not audits.

---

## 4. What does trading_sim already do, and what would it need for a credible forward test?

### Takeaway
trading_sim is already a forward-only, rule-based paper experiment with a randomized control. Every day a "claude" arm picks call or put on same-day XSP options, and a "coin" arm picks at random. It has good engineering hygiene. But it is about four trading days old, records the outcome only as option P&L, and prices orders off the indicative (non-OPRA) feed. Its ledger has unreconciled open contracts, and it has no statistics, cost model or pre-registered sample size. On the numbers in Section 2, a credible verdict on "claude beats a coin" needs hundreds of trading days, not weeks.

### Cited Findings
- Purpose: "Paper-trading experiment: same-day XSP index options, a 'claude' arm (direction picked with a one-line reason) against a 'coin' arm (random coin flip). Paper only." The code is Python standard library only. It "talks only to paper-api.alpaca.markets and data.alpaca.markets and sends no keys". The commands are `status`, `buy`, `check`, `close` and `report`, plus a `--dry-run` flag. — [README.md](/home/user/trading_sim/README.md)
- Rules:
  - Fixed "$100 per trade", using 0DTE XSP options.
  - Entry at 9:45 ET at the strike "whose ask is closest to $0.10", with contracts = floor(100 / (ask × 100)), bought with a limit at the ask. Orders are cancelled after 2 minutes ("no fill").
  - Half the contracts are offered at 5× the fill price. The rest is closed at 3:15 ET. "Never hold to expiry."
  - Quotes come from the `indicative` feed because "The `opra` feed returned 403 ('OPRA agreement is not signed')".
  - Close sells use a day limit at the bid ($0.01 if there is no bid). If unfilled after 60 s, the order is "left working".
  - Orders are tagged `claude-YYYYMMDD-<step>` / `coin-YYYYMMDD-<step>`, and missing rows are rebuilt from the tagged orders.

  — [RULES.md](/home/user/trading_sim/RULES.md)
- trade.py (778 lines) sets `FEED = "indicative"` with the comment "opra returns 403 on this account". It refuses any host other than the two Alpaca hosts. `report` prints per-arm totals: days, filled, no-fill, cost, proceeds, profit and wins. A grep found no Sharpe, benchmark, drawdown, p-value or binomial code. The claude arm's direction and reason are passed in on the command line (`buy --direction ... --reason ...`), so the decision is made outside the script. — [trade.py](/home/user/trading_sim/trade.py)
- trades.csv holds 8 rows covering 2026-11-18, -19, -20 and -23. — [trades.csv](/home/user/trading_sim/trades.csv)
  - The arms chose the **same direction on 3 of 4 days**, so they held the identical contract (704P, 678P, 676P). They differed only on 11-19 (claude 754C, coin 719P).
  - Recorded profit: claude −80, −100, −80 (total −$260); coin −80, +205, −80 (total +$45). 11-23 is still open.
  - On 11-18, "close sell rejected HTTP 403 (no quote; market order); held 10 to expiry". The coin arm's close was "never sent (script stopped after claude's 403)".
  - On 11-19 and 11-20 the close sells at the indicative bid were "filled 0/10, left working; WARNING 10 contracts still open after close", and for the coin arm on 11-19, 5 contracts.
  - On 11-19 the coin arm's half-exit was "placed" at 0.40 but recorded at a fill price of 0.57.
- Git history:
  - Trade rows are committed twice a day: "trades: buy <date>" at about 14:46 UTC (09:46 ET) and "trades: close <date>" at about 20:17 UTC (15:17 ET). The remote is a GitHub repository.
  - RULES.md and trade.py were changed on 2026-11-18 at 21:43 UTC, after the first trading day ("close: sell with a limit at the bid; treat order-rejection 403s as rejections").
  - `trade.log` is git-ignored.

  — [git log of /home/user/trading_sim](/home/user/trading_sim/.git); [.gitignore](/home/user/trading_sim/.gitignore)

### Inferences
- **The design is better than most hobby forward tests.** The rules are written down, it trades forward only, it has a randomized control arm, the morning commit records the decision about 5.5 hours before the outcome, and orders are tagged so they can be reconciled with the broker.
- **Information rate is very low.**
  - The coin matches claude's direction about 50% of the time, and on those days both arms hold the same contract, so the P&L difference is exactly zero. Only about half the days can distinguish the arms (computed: 250 trading days give about 125 informative days).
  - On top of that, $0.10 0DTE options mostly expire near zero in both directions, so option P&L is a noisy proxy for directional skill.
  - Recommendation: add columns for the XSP (or SPY) price at entry and at 3:15, and a `direction_correct` flag. Then make the **pre-registered primary test a one-sided binomial test of claude's directional accuracy against 50%**, which uses every day. Per Section 2D, detecting 55% accuracy needs about 617 trading days (about 2.4 years), and 60% needs about 153 days.
  - Keep "claude P&L minus coin P&L" (paired, bootstrap CI) as the secondary test.
  - Optionally record the quotes of the opposite-direction contract every day (a counterfactual "shadow" arm), so each day yields a paired P&L comparison.
- **The ledger needs reconciliation before any result is trustworthy.**
  - Rows flagged "still open after close" are booked as if the leftover contracts were worth $0. Their real fate (late fill, expired worthless, or auto-exercised for cash if ITM by ≥ $0.01) is not recorded, and paper exercise/expiration records arrive the next day.
  - Recommendation: add a next-morning reconciliation step against Alpaca orders, account activities and equity, and a `final_disposition` column.
- **The 11-19 fill of 0.57 on a 0.40 limit is probably a paper artifact.** It matches the documented NBBO-matching rule with no queue position. Conservative accounting would book the half-exit at the limit (0.40), which turns the coin arm's +$205 into +$120 (computed: 5 × 0.40 × 100 − 80).
- **Quotes.** Strike selection, entry limits and exit limits all use indicative quotes, which Alpaca says are "not real data". The repeated "limit at the bid did not fill" and "no quote" outcomes are consistent with a mismatch between indicative and real quotes, though not proven. Options:
  - pay for Algo Trader Plus ($99/month) and sign the OPRA agreement to get real quotes; or
  - at least log the full quote (bid, ask, timestamp, feed) behind every order and fill, and judge exits by whether they *could* have filled live.
- **The 3:15 close rationale may not apply to XSP.** Per Alpaca's FAQ, XSP 0DTE trades until 4:00 PM ET, index options "generally fall outside" the sellout logic, and far-OTM longs are not auto-liquidated. Closing at 3:15 is harmless, but the stated reason (to beat a 3:30 liquidation) may not hold for XSP.
- **Rule changes.** The close-logic change after day 1 is an execution bug fix, which is acceptable. It should be listed as a dated amendment, and each row should carry the code version (commit hash) it ran under.
- **Verifiability upgrades:**
  - Commit and push the decision (direction, reason, a hash of the data snapshot) *before* sending the order, not only after the fill.
  - Anchor commits with OpenTimestamps, and sign them.
  - Keep the raw run log (currently `trade.log` is git-ignored) or a hashed digest of it.
  - Export Alpaca order and activity history periodically.
- **Multiple testing.** Every change to the prompt or model that drives the claude arm, or any parallel variant arm, counts as a trial. Picking the best of several later inflates results, as Section 2C shows. Keep a running trial count in RULES.md.
- **Costs and real money.** Paper does not charge regulatory fees, and live per-contract costs were not verified. Subtract an estimated cost per contract.
- **Evidence threshold.** Do not consider live trading until all of the following hold:
  - the pre-registered accuracy test passes at its planned n;
  - the after-cost paired P&L versus the coin is positive with a CI that excludes zero;
  - results hold under conservative fill accounting.

  Even then, start with the same $100 size live and compare live fills with paper fills.

### Gaps
- I did not run the code or call Alpaca (by instruction). Which quotes the paper engine actually used for these fills, and what happened to the contracts flagged "still open after close", cannot be determined from the repo.
- The repo does not record how the claude arm's direction is generated (prompt, model, data access) or whether that process has changed over time. This matters for counting trials (N) and for reproducibility.
- `reports/` is empty, and there is no analysis or statistics code to evaluate.
