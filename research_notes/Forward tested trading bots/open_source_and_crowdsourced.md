# Open-source bots, crowdsourced quant platforms and individual systematic traders: who has a real forward track record?

Scope note: only forward results (live money, or paper trading run forward in time / scored on data that did not exist when the model was frozen). Backtests appear only as contrast. Research date: 2026-11-23. LLM/AI trading arenas, AI ETFs and signal marketplaces (Myfxbook, MQL5, Darwinex, Collective2, eToro) are out of scope. Reddit could not be reached by my tools (blocked), so r/algotrading items are gaps.

Verification tiers used: (A) third-party/broker-linked, platform-scored or on-chain verified; (B) regulated fund public NAV or audited; (C) peer-reviewed or preprint out-of-sample study; (D) self-reported with statements or logs; (E) self-reported marketing claim only.

## Q1. Do the major open-source frameworks (Freqtrade, Hummingbot, Jesse, OctoBot, Superalgos, NautilusTrader, QuantConnect LEAN, Lumibot, backtrader, Gekko) have published live/forward results? (strat.ninja dry-runs; Hummingbot Foundation data)

### Takeaway
None of the framework maintainers publish a forward P&L track record. Freqtrade's own docs warn that "most public strategies are not good performers" and that only dry-run (forward) testing can confirm one. strat.ninja's dry-run tracking relied on users uploading their own stats, and the domain now redirects to a parking page, so I could not find the fraction of public strategies that were profitable forward. Hummingbot publishes only volume, never operator P&L. The one framework ecosystem with platform-scored forward results is QuantConnect/LEAN's Quant League (2024–2025). It ran one quarter at a time, published only the top 3 and has now ended.

### Cited Findings
**Freqtrade (maintainers publish no results; their docs are explicitly skeptical of public strategies)**
- Freqtrade docs: dry runs "use real time data from the exchange" and are "a much more reliable indicator of **potential** performance than backtesting". They also say "Always dry run your strategy after backtesting it to see if backtesting and dry run results are sufficiently similar." — [Freqtrade Strategy Quickstart](https://www.freqtrade.io/en/stable/strategy-101/)
- The same page says "most public strategies are not good performers", "taking public strategies and using backtests as a way to assess performance is often problematic", and "Some websites that list and rank Freqtrade strategies show impressive backtest results", which should not be assumed achievable. — [Freqtrade Strategy Quickstart](https://www.freqtrade.io/en/stable/strategy-101/)
- Backtesting docs: "Backtesting will **never** replace running a strategy in dry-run mode", "only forward-testing (dry-mode) can really confirm a strategy", and "past results don't guarantee future success." — [Freqtrade Backtesting docs](https://www.freqtrade.io/en/stable/backtesting/)
- The Freqtrade site lists strat.ninja as a community "Freqtrade Backtesting Project (by Blood4rc)" and also lists "FrequentHippo – Statistics of dry/live runs and backtests (by hippocritical)". I only saw this in search snippets and did not verify either project's data. — [Freqtrade docs home](https://www.freqtrade.io/en/stable/)

**strat.ninja (the dry-run data was user-uploaded, not run by the site)**
- strat.ninja's dry-run tracking worked through a user-run script, `stratninja.py`, added to the user's own Freqtrade bot. It posts the user's own dry-run stats (profit, win rate, profit factor, max drawdown, Sharpe/Sortino/Calmar, CAGR) to strat.ninja using a personal upload token. "Only closed trades are counted", and "At least 2 closed trades are needed before the statistics will be posted." Stats re-post every 15 minutes. The README describes no independent verification. The only date shown is a sample output dated "2023-11-23". — [Bloodhunter4rc/stratninja on GitHub](https://github.com/Bloodhunter4rc/stratninja)
- When I fetched https://strat.ninja/ on 2026-11-23, it returned HTTP 302 to `ww547.strat.ninja/?tkn=…`, a domain-parking style redirect. The site's rankings and dry-run pages appear to be offline, and I could not reach the Wayback Machine with my tools. — [strat.ninja](https://strat.ninja/) (my own fetch)
- Verification tier for strat.ninja dry-run data: D at best, since these are self-uploaded bot logs with no broker link. Results are paper (dry-run) by construction.

**Hummingbot (Foundation reports volume, never operator profitability)**
- The 2019 "$ONE Makers" study (Harmony, 1 Jul – 4 Sep 2019) had 68 participants (about 43 active in late August), "143,000+ filled orders totalling $6.4 million in volume". The top 10 participants were 88% of filled volume, and the bots reached about 8% of $ONE's Binance volume in the last week of August. The Foundation states it "can't inspect the trading performance of our users directly." Profitability rests on two unquantified interviews. — [Hummingbot blog, 9 Sep 2019](https://hummingbot.org/blog/does-community-based-market-making-work/)
- Hummingbot Miner year 1 (Mar 2020 – Feb 2021) reported "$837mm of traded volume" across liquidity-mining campaigns, with about 40–50 active bots per campaign. — [Hummingbot Miner year-1 recap](https://hummingbot.org/blog/hummingbot-miner-year-1-recap/)
- The README says users "generated over $34 billion in trading volume across 140+ unique trading venues" over "the past year". It is undated and gives no methodology, so this is tier E. — [hummingbot/hummingbot GitHub](https://github.com/hummingbot/hummingbot)
- Telemetry is "aggregated, anonymized" volume metrics sent every 15 minutes. No wallet addresses or API keys are collected, so the Foundation structurally cannot compute operator P&L. — [Hummingbot DATA_COLLECTION.md (fork copy)](https://github.com/VPashkov/hummingbot/blob/master/DATA_COLLECTION.md)

**QuantConnect LEAN: Quant League, the one framework-linked forward scoreboard (tier A, platform-scored)**
- Q1 2025: algorithms were "ranked by out-of-sample live trading returns". The top three were Triton Quantitative Trading 14.88% (protective momentum with risk hedging), Imperial College London 13.54% and Stony Brook Applied Mathematics 12.97%. QuantConnect said Q2 2025 would be the first quarter ranked by out-of-sample Sharpe. — [QuantConnect forum 19032](https://quantconnect.com/forum/discussion/19032)
- Q3 2025: Lake Forest College had an out-of-sample live Sharpe of 3.93, CUHK 3.56 and QUARCC (Concordia) 3.1. The page gives no returns, drawdowns, benchmark or participant count, and does not say whether the money was paper or real. It also says "Quant League is evolving into Strategies… Q4-2025 will be the final Quant League." — [QuantConnect announcement 19630](https://www.quantconnect.com/announcements/19630/quant-league-q3-2025-results-a-close-race-between-lake-forest-and-cuhk/)
- A forum listing also carries a Q3 title "Protective Momentum Holding takes the 1st place!", which conflicts with the Lake Forest result. I could not resolve this. — [QuantConnect forum list](https://www.quantconnect.com/forum/list/7/announcements)

### Inferences
- These GitHub frameworks are execution and backtest engines. None of their maintainers runs or publishes a forward strategy record, so stars and forks say nothing about profitability. Freqtrade's maintainers say so explicitly in their docs.
- strat.ninja-style forward data was crowd-uploaded, unverified, and reported only closed trades with as few as 2 of them. Even when it was online, it was selection-biased: users choose which dry-runs to upload and can stop at any time.
- Quant League shows what "real forward results" look like at framework level. Even there, a one-quarter window, top-3-only reporting, no benchmark, and many teams competing (multiple testing) make the winners' 13–15% quarterly returns and 3–4 Sharpe ratios weak evidence of persistent skill.

### Gaps
- I could not get the fraction of strat.ninja dry-run strategies that were profitable forward, or how dry-run compared with backtest, because the site is now parked and archive.org was unreachable. I could not confirm any aggregate number. FrequentHippo's statistics were not verified.
- Jesse, OctoBot, Superalgos, NautilusTrader, Lumibot, backtrader and Gekko: I ran no dedicated search for each. No maintainer-published forward results surfaced in my searches, but that is absence of evidence from limited searching. (Gekko was archived years ago.) Lumiwealth/Lumibot and OctoBot cloud marketing claims were not checked.
- Quant League: Q2 and Q4 2025 results, participant counts, paper-vs-real status and benchmark returns were not found. A community post saying a cloned top Quant League algorithm's 2025 backtest "looked nothing like" its live results appeared only in a search snippet, and I could not pin its URL.

## Q2. Crowdsourced quant platforms with live track records (Quantopian, QuantConnect Alpha Streams, Numerai and Signals, WorldQuant BRAIN, Kaggle Jane Street real-time competition, CrunchDAO/ADIA Lab)

### Takeaway
The strongest public forward evidence on crowdsourced strategies is negative. In Quantopian's 888-algorithm study, backtest Sharpe barely predicted out-of-sample Sharpe (R² < 0.025). Quantopian's real-money fund underperformed for about 2 years and was closed in Feb 2020, and QuantConnect's Alpha Streams was shut in 2022. Numerai is the survivor. Its tournament is scored forward by design, and its fund self-reports +25.45% net for 2024 (Sharpe 2.75) after −17% in 2023. That record won JPMorgan up to $500M of capacity in Aug 2025, but no public audited NAV was found and full-year 2025 was not found. Forward-scored competitions (Kaggle Jane Street, CrunchDAO/ADIA) are genuinely forward, but they measure forecast accuracy, not trading P&L.

### Cited Findings
**Quantopian: Wiecki et al. (2016), "All that Glitters Is Not Gold" (tier C, SSRN preprint)**
- The study covers 888 Quantopian algorithms, each with at least six months of out-of-sample results. Backtest Sharpe had little predictive value for out-of-sample performance (R² < 0.025). — [SSRN 2745220](https://ssrn.com/abstract=2745220) via [Tessera summary](https://www.tesseratrades.com/learn/is-algo-trading-profitable); [Quantpedia summary](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [paper PDF](https://c.mql5.com/forextsd/forum/208/All%20that%20Glitters%20Is%20Not%20Gold%20-%20Comparing%20Backtest%20and%20Out-of-Sample%20Performance%20on%20a%20Large%20Cohort%20o.pdf)
- Per CXO's summary, in-sample backtests covered 2010–2015 and out-of-sample ran roughly June 2015 – Feb 2016. Individual backtest metrics explained about 1–2% of out-of-sample variance (R² ≈ 0.01–0.02). Non-linear ML models on backtest features reached R² ≈ 0.17. A top-10 portfolio picked by ML had a net out-of-sample Sharpe of 1.8, versus 0.7 for the top-10 picked by in-sample Sharpe. — [CXO Advisory](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies)
- The more backtests an author ran, the larger the gap between in-sample and out-of-sample performance (an overfitting signature). — [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/)

**Quantopian: real-money allocations and shutdown (performance numbers never published; tier E/D)**
- In July 2016, Steven Cohen said Point72 "will put up to $250M" behind Quantopian algorithms. Quantopian funded individual algorithms with as much as $50M (Bloomberg). — [Wikipedia: Quantopian](https://en.wikipedia.org/wiki/Quantopian)
- Quantopian's own post title reads "Quantopian funds over $50 million to a single strategy, $155 million overall". Search snippets give the $155M as cumulative base capital as of June 1, year not visible (likely 2018). — [Quantopian post](https://www.quantopian.com/posts/quantopian-funds-over-50-dollars-million-to-a-single-strategy-155-dollars-million-overall)
- In February 2020, Quantopian said it would return investors' money because its strategies underperformed. — [Wikipedia](https://en.wikipedia.org/wiki/Quantopian); [Neudata](https://www.neudata.co/alternative-data-news/quantopian-shuts-its-doors-co-founders-join-robinhood)
- CEO John Fawcett told the Boston Business Journal (20 Feb 2020) that the low-risk, market-neutral strategy had not produced results for at least two years. — [Business of Business](https://www.businessofbusiness.com/articles/how-quantopian-died-shut-down-quant-investment-robinhood/)
- The community platform went offline on 14 Nov 2020 and staff joined Robinhood. Fawcett: "Crowd-sourcing alpha was a moonshot." — [Wikipedia](https://en.wikipedia.org/wiki/Quantopian)

**QuantConnect Alpha Streams (closed; no aggregate live performance published)**
- QuantConnect discontinued Alpha Streams v1.0. Renewals were disabled, sales paused, wallet balances paid out, alpha live hosts stopped, and refunds offered to long-term licensees. — [QuantConnect forum: Alpha Streams Refactoring 2.0](https://www.quantconnect.com/forum/discussion/13441/alpha-streams-refactoring-2-0/)
- The closure date conflicts across sources. QuantConnect's own note says "Alpha Steams ceased February 2022" — [QC announcement](https://www.quantconnect.com/announcements/15944/pioneering-a-free-market-for-alpha/). StratCraft says it launched May 2018 and shut Sep 2022 — [StratCraft](https://stratcraft.ai/alpha-factory/signals-are-commodities). StratCraft also says "most signals sold zero" but gives no source, so that claim is unverified.

**Numerai: hedge fund (manager-reported, press-corroborated; between tiers B and D, since no public audited NAV was found)**
- Numerai's blog (26 Aug 2025) reports 2024 for Numerai One: +25.45% net, Sharpe 2.75 (net, rf = 0), one down month. Fees are 1% management and 20% incentive (founding class). Returns are for a "model investor" from 1 Sep 2019 paying full fees, with fees applied retrospectively. AUM grew from about $60M to $450M over three years. JPMorgan Asset Management "secured $500m in capacity". — [Numerai blog](https://blog.numer.ai/jpmorgan-secures-500m-capacity/)
- Hedgeweek (28 Aug 2025, citing Bloomberg) gives 2023 at −17%, 2024 at +25%, and 2025 YTD at about +6% net. It says the fund "has gained in every year since inception except one", reports 15 consecutive positive months per Richard Craib, and says JPMorgan's commitment of up to $500M would take AUM to "nearly $1bn over the next year". — [Hedgeweek](https://www.hedgeweek.com/quant-hedge-fund-numerai-secures-500m-jpmorgan-allocation/); [Bloomberg, 26 Aug 2025](https://www.bloomberg.com/news/articles/2025-08-26/crowdsourcing-hedge-fund-gets-500-million-jpmorgan-commitment)
- Ventureburn (21 Nov 2025): "Numerai reported $550 million in assets this year", a $30M Series C at a $500M valuation, and the 2024 return restated as 25.45% net. — [Ventureburn](https://ventureburn.com/numerai-raises-30m/)
- A 13F-derived "Q2 2026: 5.50%" for Numerai GP LLC appears on HedgeFollow. A 13F covers long US equity holdings only and is not the market-neutral fund's return, so it is not usable. — [HedgeFollow](https://hedgefollow.com/funds/Numerai+GP+LLC/Performance-History)
- Numerai's 2026 blog index (15 posts, Feb–Nov 2026) contains no fund-performance post. — [Numerai blog index](https://blog.numer.ai/)

**Numerai tournament and Signals (forward-scored by design; tier A for model scores, which are not P&L)**
- Scores resolve only on future data. A round's score is final after 20 days of returns following a 2-day lag ("20D2L", about one month). 60D2L rounds resolve about 12 weeks after submission and lock stake for that period. "Only final scores count toward live performance." Reputation is the trailing one-year average. From round 1343, CORR/MMC/BMC use the 60-day Ender target. From round 1393 (around 6 Nov 2026), Classic payouts are planned to switch to "8 × NCORR + 32 × NMMC". — [Numerai docs: Scoring](https://docs.numer.ai/numerai-tournament/scoring)
- Signals is merging into the main tournament. Signals models can stake on Numerai from 6 Nov 2026, and "All Numerai Signals stakes and models migrate to Numerai" on 1 Jan 2027. The Unity dataset (1,040 features with real tickers, released 16 Oct 2026) "doubles the NCORR of the Numerai Signals benchmark model", but no absolute numbers are given. The post contains no Signals P&L, Sharpe or payout figures. — [Numerai blog: Unifying Numerai and Signals](https://blog.numer.ai/unifying-numerai-and-signals/)

**WorldQuant BRAIN (no public forward data)**
- In the International Quant Championship, alphas count only "if they qualify for out-of-sample testing" and are scored against other participants' alphas. — [WorldQuant IQC guidelines](https://www.worldquant.com/vi/iqc)
- Consultants are paid on the quality and quantity of their alphas, under tiers WorldQuant can change. Reported earnings are "modest", and those figures are anonymous, self-reported and unverifiable. — [Quantt guide](https://www.quantt.co.uk/resources/worldquant-brain)
- WorldQuant has never published fund performance publicly. — [Wikipedia: WorldQuant](https://www.wikipedia.org/wiki/WorldQuant)

**Kaggle: Jane Street Real-Time Market Data Forecasting (final leaderboard scored on future data; tier A, but the metric is forecast R², not P&L)**
- The competition launched 14 Oct 2024 with a submission deadline of 6 Jan 2025 and a $120K prize pool. — [QuantChallenges listing](https://quantchallenges.com/challenges/jane-street-real-time-market-data-forecasting-qc-2727)
- It was "the most popular competition we found in 2025", with "over 3,700 teams". — [ML Contests 2025](https://mlcontests.com/state-of-machine-learning-competitions-2025/)
- AlphaNova reports 25,446 entrants and 4,294 submissions, and $50K for first place. These entrant and team counts are not directly comparable to ML Contests'. — [AlphaNova](https://www.alphanova.tech/blog/the-jane-street-kaggle-competition-explained)
- Models were frozen and "evaluated on fresh, real-world data that was completely unseen during training", and the final leaderboard ranks that live performance. — [AlphaNova](https://www.alphanova.tech/blog/the-jane-street-kaggle-competition-explained)
- The metric is sample-weighted zero-mean R² of responder_6. — [Kaggle competition page](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting)
- The 162nd-place private-leaderboard write-up used a 70/30 blend: an online-learning TabM neural net fine-tuned on a rolling 3–4 days of data, plus a static LightGBM. This came from a search snippet; the page body did not render. — [Kaggle write-up](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting/writeups/max-abhi-private-lb-162nd-solution)
- A CLIST standings snapshot dated 12 Jul 2025 shows many tied scores of 0.01. — [CLIST](https://clist.by/standings/jane-street-real-time-market-data-forecasting-finance-tabular-regression-custom-metric-54687226/)

**CrunchDAO / ADIA Lab (forward or held-out scored; classification, not P&L)**
- 2025 Structural Break Challenge: a winning team self-reports the $40,000 top prize among 1,767 participants and about 90% AUC. A 7th-place participant self-reports 88.34% ROC AUC "on the out-of-sample dataset". — [Winner's LinkedIn](https://br.linkedin.com/in/jvss84); [ADIA Lab challenge page](https://www.adialab.ae/structural-break-challenge)
- The 2026 "Real-Time Edition" had its final evaluation at the end of Oct 2026, with winners due at the ADIA Lab Symposium (26–28 Oct 2026). — [ADIA Lab Real-Time Edition](https://www.adialab.ae/adia-lab-x-crunch-the-structural-break-challenge-2026)
- CrunchDAO has 11k+ users and $300,000 in total prizes across 6 competitions in 2025. DataCrunch "runs continuously with prizes paid out monthly". — [ML Contests 2025](https://mlcontests.com/state-of-machine-learning-competitions-2025/)

### Inferences
- Wiecki et al. remains the single best large-sample backtest-vs-forward comparison for retail-built algorithms. It implies that a high backtest Sharpe in a GitHub README is close to uninformative about forward Sharpe.
- Every crowdsourced platform that paid for retail strategies out of real capital has either closed (Quantopian 2020, Alpha Streams 2022) or, in Numerai's case, survived by ensembling thousands of staked forward-scored signals into one meta-model, rather than allocating to individual strategies.
- Numerai's fund record is the best real-money evidence from a crowdsourced system. Caveats: it is manager-reported with model-investor accounting from Sep 2019, has no published benchmark (an equity market-neutral index or cash would be appropriate), and swung from −17% (2023) to +25.45% (2024). JPMorgan's commitment is indirect evidence that an institutional allocator's due diligence was satisfied, but it is not a public audit.
- Kaggle and CrunchDAO prove that forward-scored crowdsourced forecasting is feasible at scale. Small R² or AUC edges are not trading returns once costs and capacity are counted.

### Gaps
- Quantopian fund-level returns by year (2017–2020) and the performance of individually allocated algorithms were never published in any source I found. A Nanalyze (Feb 2018) snippet mentioned a departure citing "disappointing results" for the fund launched April 2017, but I could not verify who or what.
- Numerai annual returns for 2019 (partial), 2020, 2021 and 2022, full-year 2025, and 2026 YTD were not found from primary sources. Secondary crypto-press claims of about +20% in 2022, and of +8% net through Oct 2025 versus PivotalPath Equity Quant Index +3%, could not be tied to a primary source. Numerai's max drawdown was not found. Numerai Signals' contribution to fund P&L is unpublished.
- Kaggle Jane Street RT: the winning team, its final score and the size of the public-to-private shake-up were not found, since the Kaggle leaderboard does not render to my tools.
- ADIA Lab 2026 Real-Time Edition results were not found. WorldQuant BRAIN has no public out-of-sample or live statistics.

## Q3. On-chain strategies with a fully verifiable record (Hyperliquid HLP and user vaults, dHEDGE/Enzyme): what fraction beat holding?

### Takeaway
Hyperliquid gives the cleanest large-sample forward evidence available, all tier A and on-chain. As of 20 Nov 2026, 64% of 45,275 depositor wallets in user-run vaults were down, and depositors were −$32.3M all-time in aggregate. Vault leaders lost even more on their own stakes: −$49.8M after $6.1M of commissions. The protocol's own market-making and liquidation vault (HLP) was +$140.7M across 94,626 depositors, and only 9% of them were down. No study of dHEDGE or Enzyme managers against holding ETH or BTC was found.

### Cited Findings
**Hyperliquid user vaults: Bitquery investigation (tier A, on-chain; snapshot 20 Nov 2026, 10:25 UTC)**
- The snapshot covers 9,478 user vaults on Hyperliquid's exchange. It excludes HLP, its sub-vaults and the Liquidator vault, and does not count HyperEVM vaults. Wallet result = current holdings + withdrawals − deposits. Fully exited wallets are kept. — [Bitquery](https://www.bitquery.io/investigations/hyperliquid-vaults-depositors)
- Of 45,275 depositor wallets, 64% are down, and the aggregate is −$32.3M all-time: losers −$58.1M, winners +$25.8M. Among wallets with at least $100 gained or lost, losers outnumber winners more than 2:1. 859 wallets that lost $10k or more account for 72% of losses. Depositor losses grew by $14.0M between 27 Oct and 20 Nov 2026 alone. — [Bitquery](https://www.bitquery.io/investigations/hyperliquid-vaults-depositors)
- 2,965 leaders of vaults with depositors lost $55.9M on their own stakes, and $6.1M in commissions left them at −$49.8M. One leader ("Sifu") lost $20.9M. 11 user vaults cost depositors more than $1M each, and 6 earned depositors more than $1M each. — [Bitquery](https://www.bitquery.io/investigations/hyperliquid-vaults-depositors)
- In 465 vaults, leaders gained about $9.5M (including profit share) while their depositors lost $6.3M. — [Coindoo, 22 Nov 2026](https://coindoo.com/hyperliquid-vaults-why-the-leader-can-win-while-you-lose/), summarizing Bitquery
- Bitquery's caveats: records show net deposits only, so the percentage of capital lost cannot be computed. About half of depositors have fully exited, and some records may have been removed before snapshots began. Open positions are marked at current prices. Wallets are not people. Snapshots run from 27 Oct 2026, with a gap from 28 Oct to 12 Nov. — [Bitquery](https://www.bitquery.io/investigations/hyperliquid-vaults-depositors)
- Fee structure: leaders take 10% of profits, and depositors bear 100% of losses. The public `vaultDetails` API exposes APR, PnL history and followers for any vault. — [Hydromancer](https://hydromancer.xyz/blog/hyperliquid-vaults); [Coindoo](https://coindoo.com/hyperliquid-vaults-why-the-leader-can-win-while-you-lose/)

**HLP (Hyperliquid protocol market-making/liquidation vault; tier A)**
- HLP has 94,626 depositors, 9% of them down, with an aggregate of +$140.7M. Of the 17,929 wallets that used both HLP and user vaults, 91% are ahead in HLP (+$24.6M) and 62% are behind in user vaults (−$3.3M). — [Bitquery](https://www.bitquery.io/investigations/hyperliquid-vaults-depositors)
- HLP's cumulative profit was about $138.7M from its May 2023 launch to Oct 2026. — [EarnPark review](https://earnpark.com/en/posts/hyperliquid-vaults-hlp-review/)
- An older analysis (about early 2025) reported a 143% HLP cumulative return with a 2.89 Sharpe over its window. — [Medium: Risk & Return Analysis of HLP](https://medium.com/@RyskyGeronimo/a-risk-return-analysis-of-hyperliquids-hlp-vault-7c164cd00a0d)
- HLP can lose money: a March 2025 ETH whale liquidation cost HLP about $4M. — [Incrypted](https://incrypted.com/en/the-secret-of-hyperliquid/)

**Hyperliquid traders, for context (not vaults)**
- An analysis of 10,000 Hyperliquid accounts (Nov 2024) found 16.5% profitable, 73.8% losing and 9.7% breaking even. It is self-published on Medium, with on-chain data. — [Medium: I Analyzed 10,000 Hyperliquid Traders](https://medium.com/@envyprotocol/i-analyzed-10-000-hyperliquid-traders-the-results-are-brutal-a29adcca8c2a)

**dHEDGE / Enzyme (no systematic study found)**
- Messari's dHEDGE report says the platform ranks managers by a Sortino-based score, and that the most popular pools by AUM "often choose less efficient strategies". It is not a benchmark-relative study. — [Messari](https://messari.io/report/a-new-generation-of-dhedge-funds)
- Enzyme marketing claims its Crypto Equal Weight fund "outperformed USD by 147% since inception". That is tier E, and the benchmark is cash, not ETH. — [Enzyme (LinkedIn)](https://www.linkedin.com/company/enzymefinance) (search snippet)
- A Treno blog discusses survivor bias in dHEDGE, but the performance numbers were not visible. — [Treno](https://treno.finance/blog/crypto-hedge-funds)

### Inferences
- User vaults are USDC-denominated, so "holding" for a depositor is roughly holding USDC at about 0%. On that basis, about 64% of user-vault depositor wallets did worse than simply holding the stablecoin, and the user-vault complex as a whole destroyed value for both depositors and leaders. A comparison against holding BTC or ETH is not available.
- The one strategy with a durable, verifiable on-chain forward record is HLP. It is the venue's own market-making and liquidation book, with structural advantages (order flow, liquidations) that are unavailable to an open-source bot. That supports a "the house wins" reading rather than evidence that retail-run systematic strategies work.
- Survivorship: Bitquery keeps exited wallets, which limits survivorship bias, but vault leaderboards that sort by APR show survivors. Any "top vault" record should be checked against the full population.

### Gaps
- What fraction of vaults (as opposed to depositor wallets) beat holding USDC, BTC or ETH over fixed periods: not published. It would have to be computed from Hyperliquid's `vaultDetails` API.
- Current HLP APR: vendor snapshots in search results ranged from about −0.1% to about 3.5% in late 2026, and one vendor cited about a 22% trailing-12-month CAGR as of 2026-Q1. Sources conflicted and I could not verify them. A claim that the Oct 2025 crash added about $41.5M to HLP in one weekend could not be tied to a specific source.
- dHEDGE and Enzyme: no dataset or study comparing manager returns against ETH or BTC buy-and-hold, adjusted for survivorship, was found.

## Q4. Individuals publishing live results with code or methods (Rob Carver, futures championship winners, r/algotrading) and surveys of retail algo profitability

### Takeaway
Rob Carver is the clearest case of an open-source author with a long, consistently published live record. He uses his own pysystemtrade system and posts numbered annual reports: "year 11" in Apr 2025 and "year 12" in Apr 2026, which implies a live record since about 2014. They include bad years. He self-reports a long-run Sharpe of 0.80 against 0.52 (Man AHL) and 0.54 (SG CTA index), but the reports are tier D, with no broker statements and undisclosed capital. Championship winners such as Kevin Davey have verified one-year competition results but no public multi-year live record. No rigorous survey isolates retail algo traders. The best regulator data (SEBI, India, FY25–FY26) shows algo-flagged individuals lost ₹51,728 crore gross, while 99% of institutional profits came from algo entities.

### Cited Findings
**Robert Carver: pysystemtrade author, futures trend and carry (tier D, self-reported real money)**
- His open-source system is [robcarver17/pysystemtrade on GitHub](https://github.com/robcarver17/pysystemtrade).
- Year 11 (UK tax year to 5 Apr 2025), futures, as % of starting capital: net −16.3% (MTM −17.8%, interest +2.4%, commissions −0.29%, slippage −0.56%). He calls it his worst year in futures. Vol-adjusted benchmarks were AHL −18.2% and SG CTA −17.9% (unadjusted roughly −12% and −10%). His long-only portfolio returned +3% against a −0.1% benchmark (Vanguard 80:20), and his total portfolio −1.9%. Max drawdown was about 17% (mid-July to end-Sep 2024), "probably the worst" he has seen. Real money: he "lost a chunk of my money" and pays interest on negative cash balances. — [qoppac, Year 11](https://qoppac.blogspot.com/2025/04/annual-performance-update-returneth.html)
- Year 11 annual table (vol-adjusted, AHL / SG / Carver):

  | Year | AHL | SG | Carver |
  |---|---|---|---|
  | 2015 | 66.0% | 51.4% | 59.5% |
  | 2016 | −6.2% | −3.7% | 28.1% |
  | 2017 | −3.7% | −12.6% | 2.4% |
  | 2018 | 8.7% | −1.7% | 2.0% |
  | 2019 | 5.4% | −2.7% | 4.5% |
  | 2020 | 22.0% | 6.5% | 33.8% |
  | 2021 | 0.9% | 11.9% | −1.7% |
  | 2022 | −12.0% | 33.1% | 25.8% |
  | 2023 | 8.3% | 0.6% | −7.6% |
  | 2024 | 14.5% | 24.3% | 20.6% |
  | 2025 | −18.2% | −17.9% | −14.7% |

  Full-period CAGR (vol-adjusted): Carver 12.0%, AHL 5.9%, SG 6.4%. — [qoppac, Year 11](https://qoppac.blogspot.com/2025/04/annual-performance-update-returneth.html)
- Year 12 (to 5 Apr 2026), futures: net +23.7% (pure futures 20.7%, interest 2.7%, commissions −0.33%, slippage −0.55%). The execution algo saved about 78bp of slippage (1.34% without it). Raw tax-year benchmarks were AHL 18.1% and SG CTA 15.3%. Vol-adjusted (31 Mar – 31 Mar): AHL 30.3%, SG 29.9%, Carver 25.9%, so he was lowest of the three that year. Total portfolio +6.4%, and 0.2% without futures. The account is "pretty much at the HWM set in April 2024". — [qoppac, Year 12](https://qoppac.blogspot.com/2026/04/annual-performance-update-year-12.html)
- Long-run statistics (Year 12 post, rf = 0), AHL / SG / Carver: mean 5.6% / 4.9% / 13.8%; stdev 10.7% / 9.0% / 17.3%; Sharpe 0.52 / 0.54 / 0.80; vol-adjusted CAGR 7.7% / 8.2% / 13.0%. His correlation is 0.68 with SG CTA and 0.56 with AHL. Account curves are non-compounded, and capital is not stated. — [qoppac, Year 12](https://qoppac.blogspot.com/2026/04/annual-performance-update-year-12.html)
- Neither post gives a live-versus-backtest Sharpe comparison. Under Year 11, a commenter said a pysystemtrade backtest shows that drawdown as the worst since 1970, and Carver replied "sounds plausible". — [qoppac, Year 11](https://qoppac.blogspot.com/2025/04/annual-performance-update-returneth.html)

**Futures championship winners who publish methods**
- Kevin Davey, World Cup Trading Championship (a real-money competition run by Robbins since 1984): 2005 2nd at 148.0%, 2006 1st at 106.7%, 2007 2nd at 111.6%. He describes his method in *Building Winning Algorithmic Trading Systems*. CTE "has not audited any trading statement", and competition accounts may not represent all of a competitor's accounts. — [Complete Trader's Edge](https://completetradersedge.com/?p=235275)
- Tier: A for the competition-year results, but each is a one-year, high-leverage window. No public post-2007 live record was found.

**Retail algo-trader profitability surveys and regulator data**
- No rigorous survey exists: "We could not find a regulator dataset or peer-reviewed study that isolates retail traders who run their own algorithms." — [Tessera](https://www.tesseratrades.com/learn/is-algo-trading-profitable)
- SEBI, "Profitability of Individual Traders in the Equity Derivatives Segment (FY25–FY26)", Aug 2026, whole population: 87.7% of individual traders made net losses in FY26 (90.9% in FY25). The average loss was ₹1.47 lakh versus an average profit of ₹1.22 lakh. In FY26 only 15% of 84.2 lakh individuals used algos, and SEBI says this "overstates genuine algorithmic activity" because it includes broker auto square-offs. 99% of FPI and prop-trader gross profit came from "algo entities" (at least one algo order a year). In Chart 20 (gross P&L, FY25–FY26 combined, ₹ crore), algo-flagged individuals were −51,728 and non-algo individuals −118,396, while prop algo was +89,452 and FPI algo +44,689. I extracted these figures from the PDF; the chart's bar-to-label mapping came from the text layout. — [SEBI study PDF](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf)
- SEBI FY22–FY24 (Sep 2024): about 93% of more than 1 crore individual F&O traders lost money over three years. — [SEBI study PDF](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2024/1727086965496.pdf) via [Tessera](https://www.tesseratrades.com/learn/is-algo-trading-profitable)
- Contrast, holdout rather than forward (tier E company research): of 344,081 backtested common-strategy variants, 835 were tested on a held-back final year and 204 stayed profitable. That is 24% of those tested and about 0.06% of all variants. — [Tessera](https://www.tesseratrades.com/learn/is-algo-trading-profitable)
- Related peer-reviewed evidence, as cited by Tessera:
  - Fewer than 1% of Taiwanese day traders (1992–2006) predictably earned abnormal returns net of fees. — [Barber et al. 2014](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)
  - 97% of Brazilian futures day traders active 300 or more days lost money. — [Chague et al. 2019](https://econpapers.repec.org/paper/spawpaper/2019wpecon47.htm)
  - Published predictors earned 26% less out of sample and 58% less after publication. — [McLean & Pontiff 2016](https://doi.org/10.1111/jofi.12365)

### Inferences
- Carver's record is credible mainly because of its consistency. His numbered annual series reaches year 12, and his year-by-year table runs from 2015 to 2025. He published the −16.3% year with cost breakdowns and benchmarks; I verified only the year 11 and year 12 posts directly. It is still tier D: no statements, undisclosed capital, and vol-adjusted comparisons he chose himself. In raw annual terms, his higher returns come with higher volatility (stdev about 17% against about 9–11% for the benchmarks).
- In the SEBI data, algo-flagged individuals (about 15% of traders) made about 30% of individuals' gross losses (51,728 / 170,124). Even with the auto square-off caveat, this is direct regulator evidence against the idea that retail "algo" use converts to profits. Institutional algo desks capture the profits.
- Competition wins (World Cup) and leaderboard placements are survivor statistics drawn from many entrants. They show that verified one-year outliers exist, not that a published method has a forward edge.

### Gaps
- r/algotrading: Reddit was blocked to my tools, so I found no verified, broker-statement-backed multi-year live results and no subreddit surveys.
- Carver's account size, broker-verified statements, and the exact start date of his live record (posts go back to about 2014) were not confirmed. A secondary claim that he ran at about one-third of target risk in Year 12 is unverified ([BigGo](https://finance.biggo.com/news/f742d3965bd93566)).
- Other championship winners (for example Andrea Unger) and any multi-year audited live records of method-publishing traders were not researched.
- SEBI does not report the share of algo-flagged individuals who were profitable, only their gross P&L. Net-of-cost P&L for algo individuals was not found.
