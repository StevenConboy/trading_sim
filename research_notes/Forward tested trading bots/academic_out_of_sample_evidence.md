# Academic and Institutional Evidence: Backtest vs Live Performance, Durable Strategy Families, and Retail Trader Outcomes

Notes compiled 2026-11-23. Evidence-type tags used throughout:
**[LIVE]** = real-money funds, firms or real-time investable indices/products. **[POST-SAMPLE PAPER]** = out-of-sample or post-publication, but still hypothetical portfolios (usually gross of trading costs). **[BACKTEST/REPLICATION]** = historical simulation or re-computation of published results. **[FORWARD-SIM]** = forward-simulated (paper-traded) results with no real money.

## 1. How large is the backtest-to-live decay?

### Takeaway
Published equity anomalies lose roughly a quarter of their paper returns out of sample and about half after publication, even before trading costs. Once costs are deducted, the average published anomaly is worth about 4 bps a month. Where strategies actually went live, the haircut is larger. Bank risk-premia indices lost a median 73% of their backtested Sharpe ratio (1.20 to 0.31). Smart-beta indexes went from about +3% a year "on paper" to about −0.5% to −1% a year after their ETF launched. In 888 Quantopian algorithms, backtest Sharpe explained less than 2.5% of out-of-sample Sharpe.

### Cited Findings

#### Post-publication and out-of-sample decay of published anomalies [POST-SAMPLE PAPER]
- **McLean & Pontiff (Journal of Finance, Feb 2016), 97 cross-sectional return predictors:**
  - Portfolio returns are **26% lower out of sample** (after the original sample ends but before publication) and **58% lower post-publication**.
  - The authors treat 26% as an upper bound on the data-mining effect. They attribute the remaining ~32 points (58 − 26) to publication-informed trading.
  - Sources: [CFA Institute digest](https://rpc.cfainstitute.org/research/cfa-digest/2016/06/does-academic-research-destroy-stock-return-predictability-digest-summary); [paper PDF](https://www.gwern.net/doc/economics/2016-mclean.pdf).
  - An earlier working-paper version (82 characteristics from 68 studies) reported ~35% post-publication decay. Do not mix it with the 26%/58% figures. [Fortune, 2012](https://fortune.com/2012/11/02/academics-academia-destroys-stock-picking-strategies/)
- **Falck, Rej & Thesmar, "When Do Systematic Strategies Decay?" (Quantitative Finance 22(11), 2022; CFM working paper 2021), 72 published strategies:**
  - Anomalies tested outside their original sample keep **about half of their in-sample performance**, and Sharpe ratios fall roughly by half after publication.
  - Publication year alone explains ~30% of the cross-factor variance in Sharpe decay, and overfitting-related variables add ~15%. Arbitrage-related variables are statistically significant but add little predictive power.
  - Sources: [arXiv](https://arxiv.org/pdf/2105.01380); [EconPapers](https://econpapers.repec.org/RePEc:taf:quantf:v:22:y:2022:i:11:p:1955-1969); [CFM](https://cfm.com/why-and-how-systematic-strategies-decay/). A secondary summary quotes a 56% average post-publication decay: [Evidence Investor](https://www.evidenceinvestor.com/post/why-and-how-systematic-strategies-decay).
- **Arnott, Harvey, Kalesnik & Linnainmaa, "Alice's Adventures in Factorland" (Journal of Portfolio Management 45(4), 2019; sample Jul 1963–Jun 2018):**
  - The average factor's return decays by **about 32% after publication**. Returns stay positive rather than falling to zero.
  - The figure comes from a secondary summary. Sources: [Alpha Architect](https://alphaarchitect.com/the-factors-that-plague-factor-investing/); [paper PDF](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/Econ%20870/Arnott%2C%20et%20al%20Alices%20Adventures%20in%20Factorland%2C%202019.pdf).
- **Ilmanen, Israel, Lee, Moskowitz & Thapar, "How Do Factor Premia Vary Over Time? A Century of Evidence" (Journal of Investment Management 2021):**
  - Covers value, momentum, carry and defensive factors in six asset classes over about 100 years.
  - The premia hold up out of sample, but they are muted. Overfitting accounts for roughly a **30% decline in out-of-sample efficacy**, according to a secondary summary.
  - Factor-timing profits largely disappear once realistic data lags and costs are applied.
  - Sources: [SSRN](https://papers.ssrn.com/abstract=3400998); [Alpha Architect](https://alphaarchitect.com/2019/06/factor-investing-research-on-steroids/).

#### Multiple testing and replication [BACKTEST/REPLICATION]
- **Harvey, Liu & Zhu, "...and the Cross-Section of Expected Returns" (Review of Financial Studies 29(1), 2016):**
  - Given extensive data mining, a newly proposed factor should clear a **t-ratio above 3.0**, not the usual ~2.0. The abstract says "most claimed research findings in financial economics are likely false."
  - Sources: [NBER w20592](https://nber.org/papers/w20592); [RFS via EconPapers](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:5-68.).
  - Factor count catalogued: Linnainmaa & Roberts cite it as 314 factors ([NBER w22894](https://www.nber.org/papers/w22894.pdf)). The widely quoted "316" was not confirmed from a primary source here.
- **Hou, Xue & Zhang, "Replicating Anomalies" (Review of Financial Studies 33(5), 2020), 452 anomalies:**
  - **~65% fail** the single-test hurdle of |t| ≥ 1.96 when using NYSE breakpoints and value-weighted returns. 96% of the trading-frictions category fail.
  - With a multiple-testing hurdle of t ≥ 2.78, **82% fail**.
  - Even the anomalies that replicate have much smaller economic magnitudes than originally reported.
  - The 2017 working paper (447 anomalies) found 64% insignificant, rising to 85% at t ≥ 3.
  - Sources: [EconPapers](https://econpapers.repec.org/RePEc:oup:rfinst:v:33:y:2020:i:5:p:2019-2133.); [NBER](https://www.nber.org/papers/23394).
- **Jensen, Kelly & Pedersen, "Is There a Replication Crisis in Finance?" (Journal of Finance 2023):** 153 factors, 93 countries, 13 themes.
  - The frequentist US replication rate is **~55.6%** in the published version and 56.9% in the NBER working paper, against roughly 35% implied by Hou, Xue & Zhang.
  - Their Bayesian approach gives **82.4%** for both the US and global samples. CAPM-alpha-based rates are 83–85%; the figure differs between versions.
  - 10 of 13 themes replicate at more than 75%. The exceptions are seasonality, leverage and size.
  - Sources: [publisher's version](https://research-api.cbs.dk/ws/portalfiles/portal/95651880/theis_ingerslev_jensen_et_al_is_there_a_replication_crisis_in_finance_publishersversion.pdf); [NBER WP](https://nber.org/system/files/working_papers/w28432/w28432.pdf); [Alpha Architect (a)](https://alphaarchitect.com/factors-are-global-respectable-and-repeatable/); [Alpha Architect (b)](https://alphaarchitect.com/is-there-a-replication-crisis-in-finance/).
- **Chen & Zimmermann, "Open Source Cross-Sectional Asset Pricing" (Critical Finance Review 11(2), 2022):** 319 characteristics.
  - Regressing reproduced t-stats on the original t-stats gives a slope of 0.88 and R² of 82%.
  - **98%** of predictors that were clearly significant in the original papers reproduce with t > 1.96.
  - This shows that in-sample results can be reproduced. It does not show that they persist live.
  - Sources: [Federal Reserve FEDS](https://www.federalreserve.gov/econres/feds/open-source-cross-sectional-asset-pricing.htm); [CFR](https://nowpublishers.com/article/Details/CFR-0112).
- **Chen & Velikov, "Zeroing in on the Expected Returns of Anomalies" (JFQA 58(3), 2023), 204 anomalies:**
  - Net of effective bid-ask spreads and post-publication decay, the average anomaly's expected return is about **4 bps per month**.
  - The strongest anomalies net at best ~10 bps after controlling for data mining, and combination methods net ~20 bps. These figures exclude price impact, which would lower them further.
  - The 2020 working paper (120 anomalies) reported 8 bps.
  - Sources: [Federal Reserve FEDS](https://www.federalreserve.gov/econres/feds/zeroing-in-on-the-expected-returns-of-anomalies.htm); [JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225).

#### Overfitting statistics and research protocols
- **Bailey, Borwein, López de Prado & Zhu, "Pseudo-Mathematics and Financial Charlatanism" (Notices of the AMS, 2014):**
  - Introduces the **Minimum Backtest Length (MinBTL)**.
  - With only **5 years of daily data, no more than ~45 independent strategy variations** should be tried. Beyond that, the selected strategy is likely to show a high in-sample Sharpe ratio but a zero or negative out-of-sample one.
  - Sources: [phys.org summary](https://phys.org/news/2014-04-pseudo-mathematics-financial-charlatanism.pdf); [Bailey et al., overfitting tools paper](https://www.davidhbailey.com/dhbpapers/overfit-tools-at.pdf).
- **Probability of Backtest Overfitting (PBO), Bailey, Borwein, López de Prado & Zhu (Journal of Computational Finance, 2017):** a framework for estimating the probability that the configuration selected as best in-sample is overfit. It is presented with MinBTL as part of the authors' overfitting toolkit. [Bailey et al.](https://www.davidhbailey.com/dhbpapers/overfit-tools-at.pdf)
- **Deflated Sharpe Ratio, Bailey & López de Prado (Journal of Portfolio Management 40(5): 94–107, 2014):**
  - Deflates a reported Sharpe ratio for two sources of inflation: selection bias under multiple testing (the number of trials) and non-normal returns.
  - "Not controlling for the number of trials involved in a particular discovery leads to over-optimistic performance expectations."
  - Sources: [SSRN 2460551](https://papers.ssrn.com/abstract=2460551); [Wikipedia](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio).
- **Arnott, Harvey & Markowitz, "A Backtesting Protocol in the Era of Machine Learning" (Journal of Financial Data Science 1(1): 64–74, 2019):** a seven-part protocol for ML and conventional quant research. It covers ex-ante research motivation, accounting for multiple testing (the number of trials), data and sample choices, cross-validation and out-of-sample tests, model dynamics, complexity, and research culture. Sources: [Research Affiliates](https://www.researchaffiliates.com/insights/journal-papers/702-a-backtesting-protocol-in-the-era-of-machine-learning); [SSRN](https://papers.ssrn.com/abstract=3275654); [Alpha Architect summary](https://alphaarchitect.com/protocol-to-prevent-quants-gone-wild/).

#### Strategies that actually went live: backtest vs live
- **[LIVE] Suhonen, Lennkh & Perez, "Quantifying Backtest Overfitting in Alternative Beta Strategies" (Journal of Portfolio Management, Winter 2017; working paper Mar 2016):**
  - Sample: 215 alternative-beta ("risk premia") indices from 15 investment banks, covering 5 asset classes and 11 strategy types. Daily USD returns run from Jan 1990 to Mar 2015, with an average of 10.7 years of backtest and 4.6 years of live data.
  - **Median Sharpe ratio was 1.20 in backtest vs 0.31 live, a 73% haircut.**
  - Only 18 of 215 (~8%) did as well live as in backtest, and **65 of 215 (~30%) had a negative live Sharpe ratio**.
  - Deterioration was at least 50% in every asset class. It was worst in currencies and in event-driven, value and carry strategies. It was mildest in multi-asset and fixed income and in volatility and **trend-following** strategies.
  - The most complex strategies deteriorated about 30% more than the simplest.
  - A representative product went from a backtest Sharpe of 1.42 to 0.36 live (−75%).
  - The authors conclude the industry's 50% rule-of-thumb haircut "is not conservative enough."
  - Sources: [CXO Advisory](https://www.cxoadvisory.com/big-ideas/live-performance-of-alternative-beta-products/); [Alpha Architect](https://alphaarchitect.com/looking-at-alternatives-avoid-complexity-and-magical-backtests/).
- **[LIVE index vs BACKTEST] Huang, Song & Xiang, "The Smart Beta Mirage" (JFQA 59(6): 2515–2546, 2024):**
  - Indexes tracked by smart-beta ETFs earn about **+3% a year market-adjusted "on paper" before the ETF lists, and about −0.5% to −1% a year after**. The working paper reports +2.77% vs −0.44%; the internet appendix reports a CAPM alpha of +2.72% vs −0.63%.
  - The authors examine variation in factor premia, strategic timing and diminishing returns to scale as explanations. They conclude the evidence points strongly to data mining in index construction to attract ETF flows.
  - Sources: [JFQA (open access)](https://cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/smart-beta-mirage/35CA1CEA091A485DDA960BB2D9930BC9); [IDEAS](https://ideas.repec.org/a/cup/jfinqa/v59y2024i6p2515-2546_2.html); [Internet appendix](https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S0022109023000674/resource/name/S0022109023000674sup001.pdf).
- **[FORWARD-SIM] Wiecki, Campbell, Lent & Stauth, "All that Glitters Is Not Gold" (Quantopian, SSRN 2016):** 888 algorithms with at least 6 months of out-of-sample performance.
  - **Backtest Sharpe had almost no predictive value for out-of-sample Sharpe (R² < 0.025).** Across in-sample metrics, R² was about 0.01–0.02.
  - The more backtests an author ran on a strategy, the larger the gap between in-sample and out-of-sample Sharpe.
  - Volatility, maximum drawdown and hedging carried more predictive value than Sharpe.
  - The best single predictor was the Sharpe ratio over the last in-sample year.
  - Nonlinear machine-learning classifiers on backtest features reached R² = 0.17 on hold-out data. A portfolio built from their predictions did better out of sample (Sharpe 1.2) than one built from the highest backtest Sharpe ratios.
  - Sources: [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [CXO Advisory](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies).

#### Summary: decay ladder (compiled from the sources above)
| Study | Evidence type | Measured decay |
|---|---|---|
| McLean & Pontiff 2016 (97 anomalies) | Post-sample paper, gross | −26% out of sample; −58% post-publication |
| AHKL 2019 | Post-publication paper | ~−32% |
| Ilmanen et al. 2021 (century) | Out-of-sample paper | ~−30% attributed to overfitting |
| Falck, Rej & Thesmar 2022 (72 strategies) | Post-publication paper | ~−50% Sharpe |
| Chen & Velikov 2023 (204 anomalies) | Post-publication, net of spreads | ~4 bps a month left on average |
| Suhonen et al. 2017 (215 bank indices) | Live indices | Median Sharpe −73% (1.20 to 0.31) |
| Smart Beta Mirage 2024 | Live index after ETF launch | ~+3%/yr to ~−0.5% to −1%/yr |
| Wiecki et al. 2016 (888 algorithms) | Forward simulation | Backtest Sharpe R² < 0.025 |

### Inferences
- Treat any backtest as an upper bound. Even academically vetted, economically motivated factors lose about 25–50% of their paper performance out of sample and after publication. Product backtests built to be sold, such as bank indices and smart-beta indexes, lose about 70–100%+ once live.
- The industry's 50% haircut is a floor, not a central estimate. It is too generous for complex, many-parameter strategies from sponsors who ran many trials.
- Two independent datasets agree that complexity and search intensity predict decay: Suhonen et al. find a complexity penalty, and Wiecki et al. find that more backtests mean a larger shortfall. This matches the MinBTL and Deflated Sharpe Ratio logic. A bot vendor who cannot state how many configurations were tried gives no basis for deflating its Sharpe, so its backtest should be treated as close to uninformative.
- In Wiecki et al., backtest volatility and drawdown predicted out-of-sample behaviour better than backtest Sharpe. Risk characteristics appear more stable than return claims. When judging a bot, its backtest drawdown and volatility are more credible than its backtest return.
- The "replication crisis" debate (Hou, Xue & Zhang vs Jensen, Kelly & Pedersen and Chen & Zimmermann) is about whether in-sample results are real and reproducible. Neither camp's results imply that published factors survive live trading costs undiminished. The cost-adjusted evidence (Chen & Velikov) shows little left for the average anomaly.

### Gaps
- I did not extract a precise post-publication or out-of-sample decay percentage from Jensen, Kelly & Pedersen (2023). Their replication rates are confirmed, but their out-of-sample shrinkage estimate is not.
- The exact factor count in Harvey, Liu & Zhu (commonly cited as 316) was not confirmed from the paper itself. Linnainmaa & Roberts cite 314.
- Wiecki et al. describe the out-of-sample period as performance after the algorithm was developed. I could not confirm whether any of it was real-money trading; it appears to be simulated forward performance on the Quantopian platform.
- Harvey & Liu (2015, "Backtesting", Sharpe-ratio haircuts) and Novy-Marx & Velikov (2016, anomaly trading costs) are relevant but were not retrieved.
- The exact definition behind the PBO probability and the Deflated Sharpe Ratio formula were not reproduced from the primary papers.

## 2. Which systematic strategy families have long, real, live track records, and what persisted vs decayed?

### Takeaway
- **Trend following / managed futures** has the longest live index history of any systematic family: the SG indices date from 2000, and the Barclay CTA Index and BTOP50 are commonly dated to 1980 and 1987 (not verified here). It has persisted, but live returns run far below century-long backtests. It also has long droughts, roughly 0.4–1.6% a year over 2009/10–2019, broken by bursts: 2022 at +20% to +27%, and 2026 at about +11% to +16% year to date.
- **Market making / HFT** shows the most consistent live P&L (Virtu: 1 losing day in 1,238). The edge depends on infrastructure, and industry revenue fell about 80–85% after 2009.
- **Renaissance:** Medallion's capacity-limited record (about 66% gross and 39% net a year, 1988–2018) contrasts with the same firm's scalable public funds, which lost about 19–34% in 2020 while Medallion gained 76%.
- **Factor premia** persist on paper and, for a large, low-cost institutional trader, after costs. Typical funds and smart-beta products capture far less: value roughly halved, and often nothing from momentum.

### Cited Findings

#### Trend following / managed futures
- **[LIVE vs MODEL] Hurst, Ooi & Pedersen, "Demystifying Managed Futures" (Journal of Investment Management Q3 2013, AQR):** simple time-series-momentum (TSMOM) strategies produce large correlations and high R² with managed-futures indices and with individual managers' live returns, including the largest and most successful managers. Controlling for TSMOM drives those managers' alphas to zero. Sources: [SSRN](https://papers.ssrn.com/abstract=2333776); [JOIM](https://joim.com/?p=1179); [AQR](https://www.aqr.com/Insights/Research/Journal-Article/Demystifying-Managed-Futures).
- **[BACKTEST] Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing" (AQR, 2017):**
  - Simulated TSMOM on 67 markets, 1880–2013: **14.9% a year gross, 11.2% net of a simulated 2/20 fee, net Sharpe 0.77**.
  - Correlation is about 0.00 with US equities and −0.04 with 10-year bonds. Net returns were positive in every decade; the weakest was +1.6% for the decade starting 1910.
  - Futures markets and financing that did not yet exist are simulated in the early years.
  - Sources: [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing); [PDF](https://fairmodel.econ.yale.edu/ec439/hurst.pdf).
- **[LIVE] "Lost decade":**
  - **Barclay CTA Index ~0.8% a year over 2010–2019; SG CTA Index ~1.6% a year; AQR's live Managed Futures fund ~0.5% a year.** Source: [Universa research, Nov 2022](https://universa.net/UniversaResearch_CTAs_202211.pdf). Universa is a tail-hedging manager, a potential bias, and its table was hard to parse.
  - **SG Trend Index ~0.4% annualized over 2009–2018, with a 21.8% maximum drawdown.** Source: [Price Action Lab](https://www.priceactionlab.com/Blog/2023/02/managed-futures-trend-following/), a blog of lower rigor.
- **[LIVE analysis] Babu, Levine, Ooi, Schroeder & Stamelos, "You Can't Always Trend When You Want" (AQR; Journal of Portfolio Management, Mar 2020):**
  - Trend's weaker post-financial-crisis returns came from **fewer and smaller large market moves**. There was no evidence of a material decline in the strategy's ability to turn moves into profit, and no evidence that trend followers had become less diversified.
  - The authors see little sign of permanent structural change.
  - Sources: [AQR](https://www.aqr.com/Insights/Research/White-Papers/You-Cant-Always-Trend-When-You-Want); [Alpha Architect](https://alphaarchitect.com/trend-following-reality-you-need-trends-to-trend-follow/); [Quantpedia](https://quantpedia.com/why-did-trend-following-underperform-in-the-last-decade/?a=6080).
- **[LIVE] 2022 rebound:** the **SG CTA Index rose +20.1%**, its best year on record. The **SG Trend Index rose +27.35%**, its highest return since its 2000 launch. Sources: [Hedgeweek](https://www.hedgeweek.com/flat-december-sees-ctas-complete-record-year-2022/); [Alpha-Week](https://alpha-week.com/2022-cta-index-performance-review); [The Full FX](https://thefullfx.com/year-end-drop-fails-to-dampen-stellar-2022-for-trend-followers/).
- **[LIVE] 2023:**
  - StoneX reports the SG CTA benchmark lost "almost 3%" and the SG Trend Index lost about 3.3%. A Quantpedia description calls the year roughly flat, so the size of the loss is uncertain. [StoneX](https://www.stonex.com/en-us/insights/ctas-on-course-for-positive-january-returns/)
  - March 2023 contained two of the worst days in SG Trend history. [AlphaSimplex](https://www.alphasimplex.com/assets/files/2024.01---themes-of-2023---kaminski-and-sun.pdf)
- **[LIVE] 2025:**
  - **SG Trend +2.4%, SG CTA −0.2%, BTOP50 +2.8%.** [Aussie Turtles](https://www.aussieturtles.com/battle-of-the-trend-following-indexes-december-2025/)
  - Top Traders Unplugged gives SG Trend +2.39% and BTOP50 +2.81%. [TTU, Dec 2025](https://www.toptradersunplugged.com/trend-following-performance-report-december-2025/)
  - SG Trend was **−9.33% year to date through April 2025** and still −2.27% at the end of September before recovering. [TTU, Apr 2025](https://www.toptradersunplugged.com/trend-following-performance-report-april-2025/); [TTU, Sep 2025](https://www.toptradersunplugged.com/trend-following-performance-report-september-2025/)
- **[LIVE] Jan 2020–Dec 2025:** SG Trend +49.0% cumulative (CAGR 6.9%, max drawdown 20.4%). SG CTA +29.8% (CAGR 4.4%, max drawdown 16.3%). BTOP50 +41.2% (CAGR 5.9%, max drawdown 9.7%). [Aussie Turtles](https://www.aussieturtles.com/battle-of-the-trend-following-indexes-december-2025/)
- **[LIVE] 2026 year to date:**
  - At the end of September: **SG Trend +15.80%, BTOP50 +14.81%, against +12.75% for the S&P 500 Total Return**. [TTU, Sep 2026](https://www.toptradersunplugged.com/trend-following-performance-report-september-2026/)
  - SG CTA was +15.7% through Q3. [CNBC](https://www.cnbc.com/2026/10/06/trend-following-hedge-funds-beat-stock-market.html); [HedgeCo](https://hedgeco.net/news/10/2026/trend-following-hedge-funds-returned-15-7-through-the-third-quarter-outpacing-the-sp-500.html)
  - October reversed some of the gains: SG Trend was −0.73% for the month by Oct 16, and its year-to-date gain fell from 16.14% to 14.97% in one week. [Bayes Group](https://www.bayes-group.com/insights/cme-october-record-trend-book-2026)
  - BarclayHedge estimates as of Nov 23, 2026: **SG CTA +10.98% year to date (−2.53% month to date)**. [BarclayHedge SG CTA page](https://portal.barclayhedge.com/cgi-bin/indices/displayHfIndex.cgi?indexCat=SG-Prime-Services-Indices&indexName=SG-CTA-Index)
  - BarclayHedge's SG indices page showed SG Trend at about +11.21% year to date (−2.79% month to date) as of Nov 21. This was an estimate and was not re-verified. [BarclayHedge SG indices](https://portal.barclayhedge.com/cgi-bin/indices/displayIndices.cgi?indexID=sg)
- **[LIVE bank indices]** In Suhonen et al., trend-following and volatility strategies had the **least** backtest-to-live deterioration among bank risk-premia products. Value, carry, event-driven and currency strategies had the most. [CXO Advisory](https://www.cxoadvisory.com/big-ideas/live-performance-of-alternative-beta-products/)

#### Factor / smart-beta strategies
- **[LIVE index] Smart Beta Mirage:** smart-beta indexes went from about +3% a year before ETF launch to about −0.5% to −1% a year after. [JFQA](https://cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/smart-beta-mirage/35CA1CEA091A485DDA960BB2D9930BC9)
- **[LIVE funds] Patton & Weller, "What You See Is Not What You Get: The Costs of Trading Market Anomalies" (Journal of Financial Economics 137(2), 2020):** after implementation costs, typical mutual funds earn low returns to value and **no returns to momentum**. A working-paper version estimated momentum's implementation costs at 2.2–8.3% a year. Sources: [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:137:y:2020:i:2:p:515-549); [Duke](https://dukespace.lib.duke.edu/items/bf2d8677-7443-41bc-89e7-cd58c694838d); [working paper](https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2018/03/Weller-1.pdf).
- **[LIVE funds] Arnott, Kalesnik & Wu, "The Incredible Shrinking Factor Return" (Research Affiliates, 2017):** in factor-tilt mutual funds, realized value and market factor returns are **halved or worse** compared with theoretical factor returns. High-turnover momentum incurs high costs. This comes from a secondary summary. [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/alices-adventures-in-factorland-three-blunders-that-plague-factor-investing/)
- **[LIVE execution] Frazzini, Israel & Moskowitz, "Trading Costs" (2018):**
  - Uses about $1.7 trillion of AQR's own live trades from Aug 1998 to Jun 2016, across 21 developed markets.
  - Actual costs were **an order of magnitude smaller than earlier academic estimates**. Average market impact was just under 9 bps; the value-weighted mean was about 15 bps.
  - An earlier 2012 draft (about $1 trillion of trades, 1998–2011) used these cost measures to compute break-even fund sizes for size, value, momentum and short-term reversal strategies. The break-even figures were not retrieved here. The data come from one large, skilled trader, so they may not generalize. [NBER 2012 draft](https://conference.nber.org/conf_papers/f68262/f68262.pdf)
  - Sources: [SSRN](https://papers.ssrn.com/abstract=3229719); [Institutional Investor](https://www.institutionalinvestor.com/article/b19hkzljqkhyw0/AQR-Investor-Worries-Over-Trading-Costs-May-Be-Overblown); [Alpha Architect](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/); [Swedroe/ETF.com](https://www.etf.com/sections/index-investor-corner/swedroe-trading-cost-truths).
- **[POST-SAMPLE PAPER]** Jensen, Kelly & Pedersen find most factor themes replicate in a 93-country dataset, and Ilmanen et al. find premia hold up over a century, though muted. Sources: [JKP](https://research-api.cbs.dk/ws/portalfiles/portal/95651880/theis_ingerslev_jensen_et_al_is_there_a_replication_crisis_in_finance_publishersversion.pdf); [Ilmanen et al.](https://papers.ssrn.com/abstract=3400998)

#### Market making / high-frequency trading
- **[LIVE] Virtu Financial IPO filings (2014):**
  - The original S-1 reported **one losing trading day out of 1,238** (Jan 2009–Dec 2013), as quoted by press and forums.
  - Amendment No. 2 extended the data to Feb 28, 2014: **one losing day out of 1,278**.
  - Sources: [SEC S-1](https://www.sec.gov/Archives/edgar/data/1592386/000104746914002070/a2218589zs-1.htm); [SEC amendment exhibit](https://sec.gov/Archives/edgar/data/1592386/000104746914003675/filename2.pdf); [Irish Times](https://irishtimes.com/business/financial-services/virtu-financial-prepares-for-market-float-1.1721201); [Wikipedia](https://en.wikipedia.org/wiki/Virtu_Financial).
- **[LIVE] Baron, Brogaard, Hagströmer & Kirilenko, "Risk and Return in High-Frequency Trading" (JFQA 54(3), 2019):**
  - Data: Swedish equities on all venues, Jan 2010–Dec 2014.
  - **Relative latency accounts for large differences in HFT firms' performance.** Firms whose latency rank improved through colocation upgrades saw better performance.
  - **HFT revenue and volume concentration is high and not declining.**
  - An earlier E-mini futures draft reported high Sharpe ratios, with revenue concentrated in a few firms.
  - Sources: [EconPapers](https://econpapers.repec.org/RePEc:cup:jfinqa:v:54:y:2019:i:03:p:993-1024_00); [CFTC draft](https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf); [Brogaard 2012 deck](https://www.bankofcanada.ca/wp-content/uploads/2012/11/Session-1-Jonathan-Brogaard.pdf).
- **[LIVE industry] Decay of HFT economics:**
  - US HFT revenues fell from about **$7.2B in 2009 to about $1.3B in 2014**, per a Deutsche Bank Research estimate. Causes cited were the technology arms race, competition and the shift of trading to dark pools. [Investment Executive](https://www.investmentexecutive.com/news/industry/are-the-glory-days-of-hft-over/)
  - Revenues fell **below $1B by 2017**, according to a consultancy cited by IG. Exchange colocation fees "doubled or tripled" between 2010 and 2015. [IG](https://www.ig.com/en/trading-strategies/high-frequency-trading-explained--why-has-it-decreased--181010)
  - CNBC gave a lower peak, citing a brokerage estimate of about $4.9B in profit in 2009 falling to at most $1.25B in 2011; that figure measures profit, not revenue. [CNBC](https://www.cnbc.com/id/49413864)

#### Renaissance Technologies: Medallion vs public funds
- **[LIVE, reported] Cornell, "Medallion Fund: The Ultimate Counterexample?" (2019/2020), covering 1988–2018:**
  - Average annual return was **66.1% gross and 39.2% net** (standard deviation 31.7% gross, 20.3% net). $100 grew to $398.7M gross, a 63.3% gross CAGR.
  - Fees were 5% management plus 44% performance, per a secondary summary.
  - Cornell writes: "To date, there is no adequate rational market explanation for this performance."
  - Sources: [Institutional Investor](https://www.institutionalinvestor.com/article/b1k2fymby99nj0/Famed-Medallion-Fund-Stretches-Explanation-to-the-Limit-Professor-Claims); [SSRN copy](https://www.scribd.com/document/470291821/SSRN-id3504766-pdf); [Morningstar](https://www.morningstar.com/columns/rekenthaler-report/medallion-fund-is-like-no-other).
  - Dispute: an arXiv note argues that compounding the yearly returns is misleading because fund size changed. By its formula, the annualized compounded return is about 31.8%. [arXiv](https://arxiv.org/pdf/2405.10917v2)
- **[LIVE] 2020 divergence:**
  - **Medallion +76%.**
  - **RIEF −19%** (investor letter, via Bloomberg) or **−22.62%** (HSBC data through Dec 25).
  - **RIDA −32%** (Bloomberg) or **−33.58%** (HSBC).
  - These were the public funds' worst years. RIEF was launched in 2005 as the vehicle for outside money.
  - Sources: [Institutional Investor](https://www.institutionalinvestor.com/article/2bswms7wco7as686o8ikg/portfolio/renaissances-medallion-fund-surged-76-in-2020-but-funds-open-to-outsiders-tanked); [BNN Bloomberg](https://www.bnnbloomberg.ca/renaissance-clients-pull-out-after-firm-s-rotten-run-of-results-1.1560482); [BloombergQuint](https://www.bloombergquint.com/amp/markets/simons-makes-billions-while-renaissance-investors-fume-at-losses).
  - Clients subsequently pulled about $11B. [The Wealth Advisor](https://www.thewealthadvisor.com/Article/Renaissance-Suffers-11-Billion-Exodus-Meager-Quant-Returns)
- **[LIVE] Recent public-fund results:**
  - RIEF was **+22.7% in 2024**, its best year since 2011 (+34%).
  - In 2025, both public funds were up about 5.6% and 6.5% through July. In October 2025 RIEF fell 14.39% and RIDA 15.6%, putting both in the red for the year. RIEF rose 12.65% in November 2025.
  - Full-year 2025 figures were not verified. These numbers come from search snippets of Institutional Investor coverage.
  - Sources: [Institutional Investor (Nov 2025)](https://www.institutionalinvestor.com/article/premium/renaissances-public-funds-stage-double-digit-comeback-november); [Institutional Investor (Oct 2025)](https://www.institutionalinvestor.com/article/renaissance-suffers-huge-losses-october).

### Inferences
- **Persisted live:**
  - Trend following has persisted, but it pays like a long-volatility, crisis and inflation payoff. Returns are lumpy (2022, 2026), with multi-year flat or negative stretches (2010s, 2023, 2025).
  - Market making has persisted, with near-daily profitability for the scale leaders (shown for Virtu through Feb 2014).
  - Medallion has persisted, but it is capacity-constrained and closed to outsiders.
  - For a large, low-cost implementer, value and momentum premia plausibly survive costs: AQR's own live trading costs are about ten times below academic estimates. Typical mutual funds do not capture them.
- **Decayed or failed live:**
  - Most published anomalies lose about half their paper return, and the average is near zero after costs.
  - Bank risk-premia indices lost 73% of their Sharpe ratio.
  - Smart-beta ETF indexes turned negative after launch.
  - Momentum captured by typical mutual funds is about zero.
  - HFT industry revenue fell about 80–85% from its 2009 peak.
  - Renaissance's scalable public funds are far from Medallion and can lose 20–30% in a year.
- The century-long trend backtest shows about 11% a year net. The live decade 2010–2019 delivered about 0.4–1.6% a year. Even a genuine, economically grounded strategy can underdeliver its long-run backtest average by about 10 points a year for a decade. A live record of a few years therefore cannot separate skill from regime.
- Live trend indices offer a realistic benchmark for an automated trend bot: about 4–7% CAGR with 16–20% maximum drawdowns over 2020–2025. A bot claiming much smoother or higher trend-following returns is claiming to beat the largest professional managers.
- The persistent live edges (HFT and market making, Medallion) depend on latency, colocation, capacity limits and very large infrastructure (Baron et al.). This is evidence against retail-accessible bots reproducing them.

### Gaps
- I could not retrieve official year-by-year return tables for the SG CTA, SG Trend, BTOP50 or Barclay CTA indices. BarclayHedge pages returned only current estimates.
- I found no confirmed 2024 annual return for the SG CTA or SG Trend indices.
- I could not confirm the index inception years (Barclay CTA 1980, BTOP50 1987) or the constituent rules (for example, selection of large managers open to new investment, which creates survivorship and size bias).
- The lost-decade figures come from a CTA critic (Universa) and a blog (Price Action Lab), not from the index providers.
- I found no AQR document that directly lines up its own live fund's record against its backtest of the same strategy. The 0.5% a year for AQR's managed-futures fund over 2010–2019 comes from Universa's table.
- I did not retrieve live records for specific factor ETFs since launch, such as minimum-volatility, momentum and value ETFs.
- Medallion figures derive from data reported in a book and used by Cornell; they are not publicly audited. Full-year 2025 results for Medallion, RIEF and RIDA were not verified.
- Virtu's losing-day statistics after 2014 were not retrieved.

## 3. What happens to retail active traders, including retail algorithmic traders?

### Takeaway
Across countries, products and decades, large administrative datasets show that most retail speculators lose money:
- Among Brazilian futures day traders who persisted more than 300 days, 97% lost money.
- In India's equity F&O market, 87.7–93% of individual traders lost money (FY22–FY26).
- 74–89% of EU retail CFD accounts lost money.
- A majority of crypto app users lost money on bitcoin.
- Fewer than 1% of Taiwanese day traders were predictably profitable.

In India, profits accrue overwhelmingly to institutional algorithmic traders: 99% of FPI and proprietary-trader profits came from algo entities. I found no rigorous study of net returns for retail algorithmic or bot traders specifically.

### Cited Findings
- **[LIVE] Taiwan day traders, Barber, Lee, Liu & Odean (complete Taiwan Stock Exchange data, 1992–2006):**
  - In an average year about 360,000 individuals day trade. About 13% earn profits net of fees in a typical year, but **fewer than 1% (about 1,000 of 360,000) predictably outperform** year after year.
  - Active day traders lose about 6.8 bps a day net of fees. The top 500 prior-year traders earn 28.1 bps a day after fees.
  - Sources: ["The Cross-Section of Speculator Skill" working paper](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf); published in the Journal of Financial Markets 18 (2014) ([EconPapers](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)).
  - **The aggregate performance of day traders net of fees was negative in every one of the 15 years**, and **more than 75% of day traders quit within two years**. Many persist despite extensive losses. ["Do Day Traders Rationally Learn About Their Ability?"](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/day%20trading%20and%20learning%20110217.pdf)
- **[LIVE] Brazil, Chague, De-Losso & Giovannetti, "Day Trading for a Living?" (2019/2020):**
  - Sample: all individuals who began day trading in Brazil's equity futures market in 2013–2015. Bloomberg describes the window as 2013–2017.
  - **97% of those who persisted for more than 300 days lost money.** Only **1.1% earned more than the Brazilian minimum wage**, and only 0.5% earned more than a bank teller's starting salary.
  - Sources: [EconPapers](https://econpapers.repec.org/RePEc:fgv:eesptd:525); [EconPapers WP](https://econpapers.repec.org/paper/spawpaper/2019wpecon47.htm); [Bloomberg](https://www.bloombergquint.com/onweb/day-traders-in-brazil-study-would-ve-done-better-with-9-to-5-job).
  - A 2025 follow-up on the COVID-era surge of retail day traders concludes day trading is "systematically unfavorable" for individuals and a persistent transfer of wealth to financial institutions. [Brazilian Review of Finance](https://periodicos.fgv.br/rbfin/article/view/94291)
- **[LIVE] EU CFDs, ESMA product intervention (Mar 2018):**
  - National regulators' analyses found **74–89% of retail CFD accounts typically lose money**, with average losses per client of **€1,600–€29,000**.
  - Later renewals require each provider to disclose its own loss percentage over a 12-month calculation period.
  - Sources: [ESMA press release](https://www.esma.europa.eu/node/84933); [Decision (EU) 2018/796](https://eur-lex.europa.eu/eli/dec/2018/796/oj/eng); [ESMA renewal notice](https://www.esma.europa.eu/sites/default/files/library/esma35-43-1912_cfd_renewal_3_-_notice_en.pdf).
- **[LIVE] Retail crypto, BIS Bulletin No 69, "Crypto shocks and retail losses" (Cornelli, Doerr, Frost & Gambacorta, 20 Feb 2023):**
  - Using crypto-app data from Aug 2015 to Dec 2022, "**a majority of crypto app users in nearly all economies made losses on their bitcoin holdings**."
  - Around the Terra/Luna and FTX collapses, large holders sold while smaller retail investors bought.
  - Small holders in emerging markets such as India, Turkey, Brazil and Pakistan reportedly fared worse, per secondary coverage.
  - Sources: [BIS](https://www.bis.org/publ/bisbull69.htm); [Decrypt](https://decrypt.co/121763/bitcoin-after-2015-lost-money-bis-report); [crypto.news](https://crypto.news/crypto-winter-affected-small-crypto-investors-more-than-whales-report-shows).
- **[LIVE] US retail options, de Silva, Smith & So, "Losing is Optional: Retail Option Trading and Expected Announcement Volatility" (Review of Finance 2025; WP Dec 2022):**
  - Retail investors concentrate option buying before earnings announcements and overpay. They lose **5–9% on average around announcements, and 10–14% for high expected-volatility announcements**.
  - Losses are compounded by wide bid-ask spreads and slow closing of positions. Market makers profit from this flow.
  - Sources: [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/publications/losing-optional-retail-option-trading-expected-announcement); [MIT Sloan](https://mitsloan.mit.edu/ideas-made-to-matter/retail-investors-lose-big-options-markets-research-shows).
- **[LIVE] India equity F&O, SEBI profit-and-loss studies:**
  - **FY22–FY24 (Sept 2024 study): 93% of individual traders lost money**, with aggregate losses above ₹1.8 lakh crore over three years. [Open Magazine](https://openthemagazine.com/business/sebi-fo-loss-study-explained-why-9-in-10-retail-traders-lost-91685-crore-in-fy26); [ThePrint](https://theprint.in/economy/individual-traders-incurred-cumulative-net-loss-of-rs-1-8-lakh-crore-in-derivatives-market-in-3-yrs/2280936)
  - **FY25: more than 91% lost money.** Net losses were ₹1,05,603 crore after transaction costs, against ₹74,812 crore in FY24. [Business Standard](https://www.business-standard.com/markets/news/net-losses-of-traders-in-fo-widens-in-fy25-sebi-study-125070701221_1.html) Open Magazine's FY26 piece puts FY25 losses at about ₹1.12 lakh crore, which conflicts, possibly because of a different definition or a revision.
  - **FY26 (reported Aug 2026): 87.7% of individual traders lost money.** Aggregate net loss was ₹91,685 crore, an average of about ₹1.17 lakh per trader. Active individual traders numbered 78.6 lakh, down about 20%.
  - In FY26, about 97% of individuals predominantly bought options and about 2% mainly sold them. About 92% of individual losses came from options.
  - Of traders who lost money two years in a row and kept trading, about 90% lost again. About 85% of trader-quarters were loss-making.
  - **Algo entities generated 99% of the profits** of proprietary traders (gross trading profit about ₹44,000 crore) and FPIs (about ₹14,000 crore).
  - Source for FY26: [Open Magazine](https://openthemagazine.com/business/sebi-fo-loss-study-explained-why-9-in-10-retail-traders-lost-91685-crore-in-fy26).
- **Retail algorithmic or bot traders specifically:** a targeted search found no peer-reviewed study measuring net, live returns of retail traders using automated strategies. Results were limited to manual retail-trading studies, backtests and theses. [Search result example: retail algo strategy thesis, SSRN](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3904097_code4795560.pdf?abstractid=3904097&mirid=1). The closest large-sample live evidence is SEBI's split, in which profits accrue to institutional algorithmic traders while individuals lose. The Quantopian cohort in Section 1 shows that independent quant authors' backtests did not predict their own out-of-sample results.

### Inferences
- Base rates in these datasets put the share of losing retail speculators at roughly 70–97%. The share who are reliably profitable after costs is in the low single digits or below 1%. A bot vendor's implied claim that typical users profit runs against every large administrative dataset found.
- In derivatives markets, retail losses are mirrored by gains for professional, largely algorithmic counterparties: SEBI's 99% figure, and market makers in de Silva et al. "Algorithmic" is not itself an edge. The winning algos are institutional, with low costs, speed and market-making economics.
- Persistence data cut against the idea that traders learn their way to profitability. In Taiwan, 75% quit within two years and aggregate losses held in all 15 years. In India, about 90% of two-year losers lost again. Short-horizon win streaks, whether a bot's or a trader's, are weak evidence of skill.

### Gaps
- I could not confirm a specific percentage for the BIS bulletin. The bulletin text retrieved says only "a majority." Specific percentages circulating in press coverage were not verified, and the BIS PDF could not be downloaded.
- The FCA's own CFD loss statistics (e.g., UK 2016–2019 consultation figures), US retail forex dealers' quarterly profitable-account disclosures, and Barber et al. (2009, RFS) Taiwan aggregate-loss figures were not retrieved.
- Other retail-options studies, such as Bryzgalova, Pavlova & Sikorskaya (2023) and Bogousslavsky & Muravyev, were not retrieved.
- No study of live net returns for retail algorithmic or bot users was found. This is a genuine gap in the literature found, not just in this search.
- The exact sample sizes in Chague et al. (number of starters and persisters) were not verified, and the sample window differs between sources (2013–2015 vs 2013–2017).

## 4. How much do paper or simulated results overstate live results (slippage, fills, market impact, behaviour)?

### Takeaway
Implementation costs and behaviour open a second gap on top of overfitting. Mutual funds capture little of the value premium and none of the momentum premium that paper portfolios show. Real-world factor returns are about halved. Post-publication anomalies net about 4 bps a month after spreads, before price impact. The counter-evidence is that a large, skilled institution's own trading costs were about ten times lower than academic estimates. People who do well in simulators and then switch to real money trade more and significantly underperform.

### Cited Findings
- **Implementation shortfall concept, Perold, "The Implementation Shortfall: Paper Versus Reality" (Journal of Portfolio Management, Spring 1988, pp. 4–9):**
  - Defines the gap between a paper portfolio, assumed to trade instantly at decision prices, and an identical real portfolio built from actual transactions.
  - The gap includes explicit costs, market impact and the opportunity cost of delayed or unfilled trades.
  - Sources: [Wikipedia](https://en.wikipedia.org/wiki/Implementation_shortfall); [CFA Institute FAJ, 2006](https://rpc.cfainstitute.org/research/financial-analysts-journal/2006/implementation-shortfall); [ProQuest](https://www.proquest.com/docview/195579087).
- **[LIVE vs PAPER] The Value Line paradox:**
  - Value Line's list of #1-ranked stocks showed cumulative gains of nearly 1,300% from Dec 1988 to Jun 2004, against 311% for the S&P 500, according to Value Line. Its own real-money fund lagged.
  - The recommendations' paper returns carry no transaction costs or taxes, and high turnover generates substantial costs.
  - Source: [WSJ 2004 article hosted by NYU Stern (Damodaran)](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/articles/valperfvsownpicks.htm).
- **[LIVE funds vs PAPER] Patton & Weller (Journal of Financial Economics 2020):** typical mutual funds earn low returns to value and no returns to momentum. The working paper put momentum implementation costs at 2.2–8.3% a year. [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:137:y:2020:i:2:p:515-549)
- **[LIVE funds vs PAPER] Arnott, Kalesnik & Wu (2017):** realized value and market factor returns in factor-tilt funds are halved or worse compared with theory. This comes from a secondary summary. [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/alices-adventures-in-factorland-three-blunders-that-plague-factor-investing/)
- **Arnott, Harvey, Kalesnik & Linnainmaa (2019), as summarized:**
  - Backtests omit the market impact of capital crowding into a strategy.
  - Once paper portfolios go live, transaction costs "play a very important role."
  - A strategy that cannot be implemented as the backtest assumes will "likely fall far short" of its backtest results.
  - Sources: [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/alices-adventures-in-factorland-three-blunders-that-plague-factor-investing/); [paper PDF](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/Econ%20870/Arnott%2C%20et%20al%20Alices%20Adventures%20in%20Factorland%2C%202019.pdf).
- **[PAPER with costs] Chen & Velikov (2023):** spreads plus post-publication decay leave about 4 bps a month for the average anomaly, before price impact. [Federal Reserve FEDS](https://www.federalreserve.gov/econres/feds/zeroing-in-on-the-expected-returns-of-anomalies.htm)
- **[LIVE execution, counterpoint] Frazzini, Israel & Moskowitz (2018):**
  - Based on about $1.7T of AQR's live trades, actual costs are about an order of magnitude below earlier academic estimates, with market impact around 9–15 bps.
  - Costs matter mainly through scale and turnover. Execution quality can preserve much of the paper premium, but only one large, sophisticated trader is measured.
  - Sources: [SSRN](https://papers.ssrn.com/abstract=3229719); [Alpha Architect](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/).
- **[LIVE investable indices] Suhonen et al. (2017) and the Smart Beta Mirage (2024):**
  - Bank indices went from a backtested Sharpe of 1.20 to 0.31 live. [CXO Advisory](https://www.cxoadvisory.com/big-ideas/live-performance-of-alternative-beta-products/)
  - Smart-beta indexes went from about +3% a year to about −0.5% to −1% a year after launch. [JFQA](https://cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/smart-beta-mirage/35CA1CEA091A485DDA960BB2D9930BC9)
  - Both combine overfitting with live frictions.
- **[SIMULATOR to REAL MONEY] Anginer, Piza, Ray & Xu, "Trading Simulations and Real Money Outcomes" (Journal of Behavioral Finance 25(4): 436–448, 2024):**
  - Three kinds of stock-simulator user are more likely to open real-money accounts: more active users, those taking more risk, and those with the best stock-level (not portfolio-level) simulated performance.
  - These users then trade more actively and **significantly underperform in their real-money trades**. The authors warn that simulator users may draw incorrect inferences about their skill.
  - A secondary source describes the setting as Brazil; this was not verified.
  - Sources: [IDEAS](https://ideas.repec.org/a/taf/hbhfxx/v25y2024i4p436-448.html); [EconPapers](https://econpapers.repec.org/RePEc:taf:hbhfxx:v:25y2024i4p436-448).
- **[LAB, not trading] Real vs hypothetical stakes:** in a neuroimaging experiment, participants became more risk-averse after negative feedback as real monetary rewards grew larger. No behavioural difference appeared between large and small hypothetical rewards. Paper stakes do not reproduce real-money decision-making. [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5829218/)
- **[FORWARD-SIM]** Even with no execution frictions, forward-simulated performance of 888 Quantopian algorithms was essentially unpredictable from backtest Sharpe (R² < 0.025). [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/)

### Inferences
- The backtest-to-live gap has three additive layers:
  1. Selection and overfitting: about 25–50% for vetted academic factors, and much more for heavily searched or complex strategies.
  2. Implementation: spreads, impact, fills and turnover. These can remove most of a high-turnover premium (momentum in mutual funds) but can be small for a skilled, large trader.
  3. Behaviour: overriding the system and risk-taking that changes with real stakes.

  Paper or forward-simulated "live" results remove only part of layer 1. They do not test layers 2 and 3.
- The evidence on simulators suggests success in paper trading is a poor and even counterproductive guide. It selects people (and plausibly strategies) toward more risk and activity, which then underperform with real money.
- For judging a bot, results shown from paper trading or simulated forward testing should be classed with backtests, not with live records. Only broker-verified, real-money, net-of-cost records over a multi-year window that includes adverse regimes count as live evidence. The CTA record shows that regimes can last a decade.

### Gaps
- The specific Value Line paper-vs-real numbers in Perold (1988) could not be verified; the article is paywalled. The widely repeated Value Line comparison above uses a different period (1988–2004) from a 2004 WSJ article.
- No rigorous study was found that compares the same automated retail strategy run paper and live (fill rates, slippage versus backtester assumptions). Broker and blog claims, such as reports of large paper-trading slippage on options, were not treated as evidence.
- Novy-Marx & Velikov (2016), on which anomalies survive trading costs by turnover, and Harvey & Liu (2015), on Sharpe-ratio haircuts, were not retrieved.
- The exact sample and country of Anginer et al. (2024) were not confirmed from the full text, which is paywalled.
