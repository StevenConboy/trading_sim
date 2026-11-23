# Third-Party-Verified Trading Track Records: Signal Marketplaces, Copy Trading, Retail Bots and Real-Money Competitions

Researcher notes compiled 2026-11-23. Verification tiers used for specific systems: (A) third-party/broker-linked verified, (B) regulated platform audited, (C) academic study, (D) self-reported with statements, (E) marketing claim only. "Simulated", "hypothetical", "virtual" and "paper" results are flagged wherever they appear. Several sources are vendor, affiliate or forum pages; their reliability is noted inline.

---

## 1. How verification works on each platform, how strong it is, and how it gets gamed

### Takeaway
Most "verification" proves only that the trades shown happened on some broker account (Myfxbook, MQL5, exchange leaderboards). It does not prove that the account is representative, real money, or sensibly sized. The main loopholes are:
- **Selection:** running many accounts or portfolios, closing or deleting the losers, and choosing a custom start date.
- **Demo or virtual capital.**
- **Misleading metrics:** for example, Myfxbook "Gain" versus absolute gain.
- **Hidden tail risk** from grid and martingale systems.

The strongest records come from a regulated broker's own books with real money (eToro, Darwinex) and from real-money contests. Even these have caveats:
- Darwinex's risk engine rescales results.
- Darwinex Zero traders trade virtual capital.
- Collective2 calls all of its results hypothetical.
- The World Cup lets an entrant run several accounts and ranks only the best one.

### Cited Findings

**Myfxbook**
- Myfxbook has two separate checks:
  - **"Track Record" verification** shows that "the account's trading history shown on Myfxbook matches the account's trading history provided by the broker on the trading platform". It requires a valid account number, investor (read-only) password, broker and server — [Myfxbook help: Why Verify?](https://www.myfxbook.com/help/verification)
  - **"Trading Privileges" verification** asks the publisher to place a pending order that matches a generated authorization password: "Next time your account updates on Myfxbook, our system will detect the pending order and will compare it to the generated authorization password. If they are identical, your Trading Privileges will be verified." This proves the publisher controls the account. It does not prove the account is profitable or real money — [Myfxbook help](https://www.myfxbook.com/help/verification)
- A community checklist (EarnForex forum, post by QTH108, 25 Jan 2019) lists these red flags and tricks:
  - No green "Track record verified" or "Trading privileges verified" ticks.
  - A server labeled "Other (MT4)", meaning no real broker is identified. A custom server that imitates MT4 can feed fake results.
  - The **"Gain" vs "Absolute gain" gap.** Gain is chain-linked from the initial deposit, so a tiny first deposit followed by much larger deposits can show "100 000%" while absolute gain stays under 100%.
  - A **"custom start date"** banner, which lets the publisher "pick the best moments to create a nice performance graph".
  - Uploaded backtests that look like live results.
  - "Private" history and lot sizes.
  - A user warned (Aug 2019) of "a video going around where you can fake 'real accounts'".
  - Source: [EarnForex thread](https://www.earnforex.com/forum/threads/ways-to-recognize-fake-and-real-accounts-on-myfxbook.33417/)

**FX Blue**
- FX Blue Live publishes account history through a Publisher EA running inside MT4/MT5, or through "account sync". The MT5 publisher refreshes every 5 minutes by default, or when positions open or close — [FX Blue MT5 Publisher user guide](https://publisher.fxblue.com/appstore/u15/mt5-publisher/user-guide); [FX Blue Live](https://www.fxblue.com/live)
- I found no FX Blue equivalent of Myfxbook's verified badges. In the material reviewed, nothing confirms that a published statement belongs to the person promoting it. FX Blue should therefore be treated as an unverified self-published statement unless the broker or account is otherwise confirmed — same sources as above, plus absence of any verification documentation.

**MQL5 Signals (MetaQuotes, broker-linked MT4/MT5 accounts)**
- Every signal is labeled "Trading mode: demo or real". MetaQuotes itself warns that providers "can take much greater risks on demo accounts". Subscriber-fund totals count only real accounts — [MetaTrader 5 Help: Signal monitoring](https://www.metatrader5.com/en/terminal/help/signals/signal_monitoring)
- Statistics shown include:
  - **Growth:** "Deposit growth in percentage value... excluding deposits and withdrawals".
  - **Maximal drawdown:** "the largest balance or equity drop from the local maximum".
  - **Algo trading:** "the share of deals performed using trading robots or scripts". This lets you filter for bots.
  - **Weeks** since the first trade, plus a "Reliability" score.
  - Source: [MetaTrader 5 Help](https://www.metatrader5.com/en/terminal/help/signals/signal_monitoring)
- The showcase shows only "the top one thousand signals by rating". A trade can be "canceled", which resets its profit or loss to zero and moves the amount into a separate balance operation. There is no formal minimum history; users are told to "Be careful subscribing to too young signals" — [MetaTrader 5 Help](https://www.metatrader5.com/en/terminal/help/signals/signal_monitoring)
- An MQL5 signal provider's blog (Aller Uja, 19 Oct 2026) explains survivorship with an illustrative, not measured, example. Of 20 signals, 16 hit −100% and drop off the list. The 4 survivors average +23.75%, but all 20 starters average −75.25%. The author suggests checking how many signals are older than two years. The author also says they closed 3 of their own signals (Techno Foundation, Techno Composite, Techno SteadyFlow) since late August 2026 and pulled one EA from the Market "after its live account fell behind its test results" — [MQL5 blog](https://www.mql5.com/en/blogs/post/777995)
- MQL5 forum anecdotes (not audited):
  - Many "real" accounts are cent accounts or have deposits under $1,000.
  - The top five providers held about 53% of all subscribers (1,781 subscribers), in an undated user tally.
  - Source: [MQL5 forum, signals revenue thread](https://mql5.com/en/forum/409776/36243720). The exact post behind each claim was not pinned down, so treat both as anecdotal.

**Darwinex (DARWINs)**
- Darwinex is the trading name of Tradeslide Trading Tech Ltd. It is FCA-authorised, Firm Reference Number 586466; the FCA's own clone-firm warning lists the genuine firm's details. Darwinex also operates through Sapiens Markets EU (Spain, CNMV) and Tradeslide Global (Seychelles, FSA) — [Darwinex help: where and how is Darwinex regulated](https://help.darwinex.com/where-and-how-is-darwinex-regulated); [FCA clone warning](https://www.fca.org.uk/news/warnings/darwinexitltd-clone-fca-authorised-firm)
- A DARWIN "automatically replicates trades opened/closed by the trader" in the signal account. A risk engine then resizes positions to a 3.25–6.5% target monthly VaR, so "the results of the signal account and associated DARWIN may differ". In Darwinex's example, a signal account at 40–65% monthly VaR maps to a DARWIN at 3.25–6.5%. The risk engine "standardizes the risk it does not eliminate risk" — [Darwinex Zero docs: DARWIN vs signal account](https://darwinexzero.document360.io/docs/difference-darwin-and-signal-account); [risk engine](https://darwinexzero.document360.io/docs/risk-engine); [Darwinex help](https://help.darwinex.com/darwin-vs-its-underlying-trading-strategy)
- **Darwinex Zero** is a monthly subscription in which traders run a *virtual* account. Equity is typically $100,000, or $1M for futures. The DarwinIA "seed capital allocations are notional (or virtual) allocations" that pay performance fees. DARWINs that meet the criteria can later be opened to real third-party investor capital — [MQL5 blog on Darwinex Zero](https://www.mql5.com/en/blogs/post/773634); [Darwinex Zero docs](https://darwinexzero.document360.io/docs/understanding-capital-allocation); [EarnForex review](https://www.earnforex.com/forum/threads/darwinex-zerio-review-how-to-get-funding-for-your-trading-strategy.54694/)
- Darwinex's D-Score "assesses the quality of a DARWIN's return curve over the past five years". The Experience attribute needs at least 12 D-Periods to score 10/10 — [D-Score](https://help.darwinex.com/d-score); [Experience attribute](https://help.darwinex.com/experience-attribute)

**Collective2 (C2)**
- C2 states that all results displayed on the site must be regarded as hypothetical, and that real-account results can differ, usually for the worse. For strategies with no subscribers or AutoTraders, results are best-guess estimates from quote-feed data — [C2 support: why hypothetical](https://support.collective2.eu/portal/en/kb/articles/why-hypothetical-results-and-performance); [C2 hypothetical execution technical note](https://collective2.com/hypo_technical)
- What C2 does get right is real-time publishing: publishers send signals live and cannot submit historical (backfilled) records. Some strategy pages show how many trades were placed in real brokerage accounts (one example showed 41). C2 is an NFA member — [C2 standard strategy-page disclaimer, example page](https://collective2.com/details/132920574); [another example](https://collective2.com/details/100866695). I saw this through search extracts and did not confirm which page carries which line.
- The C2Star program was created after February 2018. Managers pay an entry fee and trade under "tight risk-control parameters", and C2 guarantees them "$1,000 per month minimum". The C2Star page still says "All performance results are hypothetical" and "Participating in C2Star does not mean strategies are 'low-risk'" — [C2 blog](https://trade.collective2.com/boring-trading-strategies-nice-during-crazy-times); [C2Star page](https://docs.collective2.eu/selector/c2star_certified)

**eToro (Popular Investors / CopyTrader)**
- eToro is itself the broker ("an online retail broker"), and researchers have studied its own logs of individual and mirrored (copied) trades. Leader and copier statistics therefore come from the broker's own execution records, not from statements users upload — [arXiv 2507.01817, describing eToro data](https://arxiv.org/html/2507.01817)
- Popular Investor (PI) payments are tied to assets under copy. Payment "will result in the payment being revoked" for "breaching leverage restrictions or risk score, not meeting the equity requirements". The 2015 rules required a risk score of 6 or less; a third-party summary lists a maximum daily risk score of 7 per tier. PIs are downgraded if they fall below a tier's requirements — [eToro Popular Investor page](https://etoro.com/popular-investor); [FF News 2015](https://ffnews.com/newsarticle/etoro-introduces-new-copy-trading-requirements-amid-increasing-popularity); [TradersUnion](https://tradersunion.com/brokers/fond/view/etoro/etoro-popular-investor/)

**ZuluTrade**
- NFA settled a 2011 complaint against ZuluTrade with a $10,000 fine. The NFA document states that Zulu "has a history of regulatory problems" — [NFA regulatory action](https://www.nfa.futures.org/BasicNet/regulatory-actions-detail-doc.aspx?docid=4323)
- A CFTC settlement over accounts from sanctioned countries is reported as a $150,000 penalty plus $80,000 disgorgement — [ForexBrokerz](https://www.forexbrokerz.com/news/cftc-fines-zulutrade-accepting-accounts-from-iran-sudan-syria)
- A consumer review notes that ZuluTrade does not vet providers and that signal providers may trade demo accounts with no equity at risk — [Forexop](https://forexop.com/how-to-profit-on-zulutrade/)
- ZuluTrade changed provider pay so that rebates earned in a month with negative overall P&L are not paid — [Finance Magnates](https://www.financemagnates.com/forex/brokers/zulutrade-pay-signal-providers-profitable-months-charged-nfa/)

**Crypto exchange copy trading (Binance/TraderWagon, Bybit; similar designs on OKX, Bitget, MEXC)**
- **Kawai et al. (CHI 2024)**, using TraderWagon (executed on Binance Futures) and Bybit data from Oct 2022 to Aug 2023 — [Kawai et al., CHI '24 PDF](https://www.andrew.cmu.edu/user/nicolasc/publications/Kawai-CHI24.pdf); [ACM DL](https://dl.acm.org/doi/full/10.1145/3613904.3642715)
  - On TraderWagon a leader can publish up to six portfolios, each with its own metrics. Leaders "can close losing portfolios and open new ones at their discretion, which allows them to establish a better performance history by rapidly clearing underperforming portfolios".
  - Portfolios are short-lived: median 2.9 days, average 16.1 days.
  - "there is absolutely no performance or qualification requirements to become a leader", yet about USD 10,000 is entrusted to each active leader portfolio.
  - TraderWagon pays leaders 10% of copiers' profits plus 10% of the transaction fees. Bybit pays 10–15% by level: Cadet 10% with up to 100 copiers, Gold 15% with up to 2,000 copiers.
- Binance lead traders can keep up to 30% of followers' realized profits. As on other profit-share platforms, leaders share in profits but not in losses — [BitDegree Binance copy-trading guide](https://www.bitdegree.org/crypto/tutorials/binance-copy-trading); [Kawai et al.](https://www.andrew.cmu.edu/user/nicolasc/publications/Kawai-CHI24.pdf)

**Bot platforms (3Commas, Pionex, Cryptohopper, Bitsgap)**
- **October 2022:** FTX users reported unauthorized trades in DMG pairs. FTX blamed leaked 3Commas API keys, while 3Commas blamed phishing sites posing as 3Commas — [The Block](https://www.theblock.co/post/179237/ftx-api-keys-3commas-exploited); [Cointelegraph](https://cointelegraph.com/news/3commas-ceo-confirms-api-key-leak-following-warning-from-cz)
- **28 Dec 2022:** Binance CEO CZ told users to disable any API key ever entered into 3Commas. 3Commas CEO Yuriy Sorokin confirmed the leaked files: "the data in the files is true". He later said there was "hard evidence that phishing was at least in some part a contributory factor". 3Commas asked exchanges to revoke all connected keys — [Cointelegraph](https://cointelegraph.com/news/3commas-ceo-confirms-api-key-leak-following-warning-from-cz)
- **Reported losses (single sources):** one FTX user lost $1.26M; the FBI was reportedly investigating — [CryptoPotato](https://cryptopotato.com/scam-alert-ftx-user-lost-1-26m-through-3commas-api/); [Finance Magnates](https://www.financemagnates.com/cryptocurrency/fbi-is-reportedly-investigating-3commas-api-leak/)
- **ForkLog/HAPI estimate:** about $14.9M across 24 confirmed victims. The same piece also cites $18.3M for six victims who lost more than $1M each, which looks internally inconsistent and was not cross-checked — [ForkLog/HAPI](https://forklog.com/en/news/api-key-leaks-and-exchange-inaction-a-hapi-analysis-of-the-3commas-incident)
- I found no independent verification scheme for bot-marketplace performance claims (3Commas marketplace, Cryptohopper marketplace, Pionex or Bitsgap bot statistics). Cryptohopper's own material only carries a generic "past performance is not indicative" warning — [Cryptohopper 2022 review](https://cryptohopper.com/news/8509-2022-year-in-review-part-2)

**Demo-account fraud dressed up as a track record**
- The CFTC's customer advisory "AI Won't Turn Trading Bots into Money Machines" (Jan 2024) describes the Mirror Trading International case:
  - Steynberg "stole more than $1.7 billion in bitcoin from at least 23,000 people".
  - He "created fake customer accounts and balances using MetaTrader demo accounts. In reality, very little money was actually traded."
  - Source: [CFTC advisory](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html); [CFTC release 8854-24](https://www.cftc.gov/PressRoom/PressReleases/8854-24)

### Inferences
- **Ranking of verification strength (my assessment from the facts above):**
  1. **Regulated broker's own books with real money:** eToro PI stats and Darwinex DARWINs that hold real investor capital. Caveats: DARWIN returns are risk-rescaled, not the trader's raw P&L, and Darwinex Zero signal accounts are virtual.
  2. **Real-money contests run through organizer-introduced brokers.** Caveat: the World Cup lets an entrant run several accounts and ranks only the best; see Q5.
  3. **Broker-linked automated monitoring:** MQL5 real-mode signals, and Myfxbook accounts with both badges at a named broker. These prove the trades happened, but say nothing about how many other accounts exist.
  4. **Exchange copy-trading leaderboards.** The data comes from the exchange's own records, but leaders can close portfolios at will and nobody is vetted.
  5. **Platform-tracked but hypothetical fills:** Collective2.
  6. **EA-published statements without a badge:** FX Blue.
  7. **Vendor claims.**
- **Where the gaming happens:** every listed gaming method works *within* "verified" data, because verification covers one account at a time, not the full set of accounts a provider runs. Methods seen across platforms:
  - Multiple accounts and portfolios (TraderWagon allows 6 per leader; the World Cup ranks your best account).
  - Closing or deleting losers (TraderWagon median portfolio life of 2.9 days; MQL5 −100% signals fall off the list).
  - Custom start dates (Myfxbook).
  - Gain-metric inflation through deposit timing (Myfxbook).
  - Demo or virtual capital (MQL5 demo signals, ZuluTrade providers, Darwinex Zero, MTI's fake MetaTrader balances).
  - Tail-risk strategies (grid or martingale) that look smooth until they blow up; see Q3.
- **Data most useful for filtering bots specifically:** MQL5's "Algo trading %" field is the only platform-level label I found that separates robot-executed trades from manual ones.
- **Practical minimum due diligence implied by these findings:**
  - Real-money account at a named, regulated broker.
  - Both Myfxbook badges, or an MQL5 "real" label.
  - No custom start date.
  - Judge on absolute gain and equity drawdown, not Gain or win rate.
  - Ask for every account the provider has ever published.
  - Look for at least 3–5 years of history spanning a crisis.

### Gaps
- Myfxbook's and FX Blue's help pages returned 403 or had no badge documentation, so the Myfxbook wording comes from search extracts of the help page. I could not confirm whether Myfxbook now blocks demo accounts from receiving badges; one forum claim says a demo account showed a privileges badge, which is unverified.
- I did not find the current official C2Star requirements page (/c2star/showRequirements), Binance, OKX or Bitget lead-trader eligibility rules, or 3Commas, Pionex, Cryptohopper or Bitsgap documentation on how (or whether) their marketplace bot statistics are verified.
- I could not confirm the exact current eToro PI requirements; third-party summaries conflict on the risk-score caps.
- I found no primary source for any regulator finding that ZuluTrade providers trade demo accounts. The claim comes from a review site.

---

## 2. Aggregate statistics: what fraction of verified bots, systems and copy-trading leaders survive and stay profitable

### Takeaway
No platform I found (MetaQuotes/MQL5, Myfxbook, Darwinex, Collective2, eToro, Binance, Bybit) publishes 1-, 3- or 5-year survival or profitability rates for its signals, systems or leaders. The independent evidence consistently points to short lives and weak persistence:
- Crypto copy-trading portfolios have a median life of 2.9 days, and "Gold" leaders collapse within about a week of promotion.
- eToro trader performance on one day does not predict later performance, and copiers underperform non-copiers.
- wikifolio signal portfolios show no alpha.
- In a C2 forum check, none of 19 strategies aged five years or more avoided a losing calendar year.
- Regulated CFD disclosures show about 50–55% of eToro retail CFD accounts lose money.

### Cited Findings

**Crypto exchange copy trading**
- Kawai et al. (CHI 2024), TraderWagon/Binance and Bybit, Oct 2022–Aug 2023 — [CHI '24 PDF](https://www.andrew.cmu.edu/user/nicolasc/publications/Kawai-CHI24.pdf)
  - TraderWagon leader portfolios lived a median 2.9 days (average 16.1 days).
  - Copiers "overwhelmingly follow leaderboard default rankings", but "neither of the ranking choices is directly correlated with long-term performance". Bybit's rankings "reflect leader popularity more than actual performance, and are poorly correlated with future returns".
  - Bybit "Gold"-level portfolios start to fall in the rankings as early as two days after promotion, and "the majority collapses about six days later". Copiers profit for about a week, then their P&L "plummets and even goes negative". "the bottom 25% Gold portfolios lead to losses of more than USD 15 000 within ten days of their promotion to Gold."
  - Conclusion: "often, positions collapse shortly after they appear on the leaderboard and start being extensively copied."
- **YieldFund study (published 24 Nov 2025; not peer reviewed; manual snapshot of public profiles; 90-day window; data gathered Oct 2025)** — [YieldFund](https://www.yieldfund.com/news/is-copy-trading-profitable-a-90-day-multi-exchange-study)
  - Sample: 1,486 leaders and 100,236 copier outcomes on Binance, Bybit and MEXC.
  - Overall: 48.48% of copier outcomes were profitable. 97.04% of leaders were positive on their own P&L, but only 43.61% produced positive P&L for their followers.
  - Binance: 66.50% copier win rate; 72.45% of leaders positive for followers.
  - Bybit: 43.65% copier win rate; 40.34% of leaders positive for followers.
  - MEXC: 57.79% copier win rate, but aggregate follower P&L of −210,040 USDT.
  - Fees, funding and slippage are not broken out. The sample covers only leaders still listed, so it carries survivorship bias.

**eToro and social-trading academic evidence**
- **eToro data, mostly FX, Apr–Oct 2013, 164,634 traders (arXiv 2507.01817)** — [arXiv 2507.01817](https://arxiv.org/html/2507.01817)
  - Mean return per trade was −7.67 bps.
  - Mirror (copy) traders averaged −10.98 bps, against +1.15 bps for traders who did not mirror.
  - Mirrored trades averaged −61.24 bps, against −6.88 bps for trades people opened themselves.
  - Performance autocorrelation matches a shuffled null model, so a trader's performance on one day does not predict later performance.
  - Copiers chose whom to copy mainly on popularity (logit coefficient 15.68), not performance (0.34). The correlation between popularity and 30-day performance was 0.11.
- **Event study on 500 certified eToro traders (Finance Research Letters, 2026)** — [IDEAS/RePEc abstract](https://ideas.repec.org/a/eee/finlet/v108y2026ics1544612326010093.html)
  - Abnormal returns of about +2% in the 10 trading days *before* a jump in popularity, "but no persistence afterward".
- **Configurational analysis of 16,964 eToro investment observations (Journal of Business Research)** — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0148296317305106)
  - Trader experience and imitation, combined with low risk, are what explain good performance.
- **Gemayel & Preda (JEBO, 2018), anonymized social trading platform** — [IDEAS](https://ideas.repec.org/a/eee/jeborg/v154y2018icp175-190.html)
  - Trade leaders who are publicly observed show a weaker disposition effect than traditional traders, which the authors read as protecting a public record.
- **Apesteguia, Oechssler & Weidenholzer, "Copy Trading" (Management Science 66(12):5608–5622, Dec 2020)** — [EconPapers](https://econpapers.repec.org/RePEc:inm:ormnsc:v:66:y:12:i:2020:p:5608-5622)
  - This is a lab experiment, not platform data.
  - Showing subjects others' performance increased risk-taking, and letting them copy increased it further. The authors conclude that copy trading encourages excessive risk-taking.

**wikifolio / ayondo (German social-trading certificates)**
- **Oehler, Horn & Wendt (2016)** — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1057521916300825); [IDEAS](https://ideas.repec.org/a/eee/finana/v46y2016icp202-210.html)
  - 1,084 wikifolio certificates issued in 2012–2013; on average they did not beat the market, with a mean monthly return of +0.09%.
- **Dorfleitner et al. (2018)** — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S106297691730248X)
  - On ayondo and wikifolio, "highly active trading behavior is negatively related with the returns" and there is no wisdom-of-the-crowd effect.
- **Oehler & Schneider (2023)** — [Springer](https://link.springer.com/article/10.1007/s11846-022-00560-6)
  - wikifolios "neither under- nor outperform the equity benchmark".

**Collective2**
- **Forum check (Aug 2023)** — [C2 forum](https://forums.collective2.com/t/are-there-any-c2-strategies-that-stay-profitable/16231)
  - A user screened C2's "Old Timers" leaderboard (strategies aged 5 years or more): "There were zero strategies that didn't have at least one calendar year with a net loss", out of 19 survivors on the leaderboard.
  - Another user said they had simulated "more than 700-800 strategies in the last few years… all of them failed". This is anecdotal.
  - C2 CEO Matthew Klein replied: "We have strategies on this site that have been around for 15 years... they're generally positive." He gave no survival rate.
- **February 2018 "Volmageddon"** — [C2 blog](https://trade.collective2.com/boring-trading-strategies-nice-during-crazy-times)
  - C2 had "nearly $100 million dollars of assets under management" when "Many of the popular strategies on Collective2 blew up", with "about $30 million dollars" leaving the platform. The outflow mixed losses and withdrawals.

**Darwinex**
- **Official counts and claims**
  - Darwinex's "All DARWINs" listing showed 10,786 DARWINs; no date or profitable share is given — [Darwinex All DARWINs](https://www.darwinex.com/all-darwins)
  - The Hall of Fame page says "more than $55M allocated to DARWIN portfolios" — [Darwinex Hall of Fame](https://www.darwinex.com/trading/hall-of-fame)
  - A review relays a self-reported €682.53M invested in trader strategies and €15.55M paid out in profits; this is unverified — [EarnForex](https://www.earnforex.com/forum/threads/darwinex-zerio-review-how-to-get-funding-for-your-trading-strategy.54694/latest)
- **Third-party estimates (they conflict and use different populations)**
  - 66% of the public Darwinex Zero accounts one review site tracks are "profitable overall" — [Algo Trading Space](https://algotradingspace.com/darwinex-review-unveiling-the-potential-of-copy-trading)
  - 56% of Darwinex traders are losing money as of May 2026 — [Nathan Tradeus](https://nathantradeus.com/en/posts/capital-efficiency-ratio-trading/)

**MQL5 / Myfxbook**
- I found no measured survival statistics. The only MQL5 survivorship figures are illustrative: 4 of 20 survive, and survivors average +23.75% while the full group averages −75.25% — [MQL5 blog, 19 Oct 2026](https://www.mql5.com/en/blogs/post/777995)
- A public scraper exposes each signal's real/demo flag and statistics, which would make a proper survival study possible — [Apify MQL5 signals scraper](https://apify.com/nick.i/mql5-signals-scraper.md)

**Regulated, platform-wide loss disclosures (verified by regulation, covering all retail CFD accounts, not copy traders specifically)**
- eToro's mandated risk warning reads about 50–55% depending on the entity and date: 51% for eToro UK, the lowest of 49 brokers in one study; 52% (UK) and 55% (Europe) on other pages — [BrokerRank retail loss-rate study](https://brokerrank.net/research/retail-loss-rates); [InvestingInTheWeb eToro review](https://investingintheweb.com/reviews/etoro-review)

### Inferences
- Across every data source with real executions (exchange data, eToro broker data, wikifolio certificate prices), **past rank or return is a poor predictor of future returns for copy leaders**. The mechanisms are the ones in Q1: copiers chase visible rankings, and leaders earn profit share with no downside, so they are paid to take risk and to discard failures.
- The CHI '24 portfolio-life figures (median 2.9 days) imply that on crypto exchanges, a "1-year survival rate" of *portfolios* is close to meaningless. The relevant unit is the *leader across all of their portfolios*, and no exchange exposes that history.
- **The big caveat on YieldFund's "97% of leaders profitable":** leaders' own P&L is overwhelmingly positive while only about 44% deliver profits to followers. This gap fits an entry-timing and selection effect, where followers arrive after the run-up, as the Bybit Gold-promotion finding also shows.
- **Rough base rate for systems sold on track records.** My rough working assumption from the evidence:
  - A minority of strategies listed on any given day will still be listed and profitable a few years later.
  - Essentially none of them avoid losing years.
  - No platform publishes the denominator (all strategies ever listed) needed to state a precise percentage.

### Gaps
- **No published 1-, 3- or 5-year survival or profitability rates** for MQL5 signals, Myfxbook systems, Darwinex DARWINs, Collective2 strategies, eToro copy leaders, or Binance, Bybit, Bitget or OKX leaders. Computing them would require scraping full listings including delisted entries; MQL5 is the most tractable, since listings carry a real/demo flag and history in weeks.
- A frequently repeated claim that "fewer than 10% of top-ranked eToro traders maintained top-quartile performance across consecutive 12-month periods (2019 study)" appeared only on a secondary blog. I could not find the original study, so treat it as unverified.
- I found no academic study using ZuluTrade, Myfxbook, MQL5, Darwinex or Collective2 data on performance persistence, and none on Bitget or OKX leaders. Gemayel & Preda's platform is anonymized.
- The Darwinex third-party profitability figures (66% vs 56% losing) cannot be reconciled: they cover different populations, dates and definitions.

---

## 3. Specific systems with long verified real-money records, and famous blow-ups of "verified" performers

### Takeaway
Long (5+ year) real-money records that you can verify with full metrics are rare in public sources. The best-documented FX example is a Waka Waka EA user account on Myfxbook: real money since June 2018, but with a 66.5% maximum drawdown. Another real account running the same grid EA rose about +400% and then went to zero in February 2022. Contest records (Davey, Unger, Williams) are real money but cover only one year each. Most AI/bot vendor "track records" are simulated or virtual.

### Cited Findings

**Specific systems**

| System / account | Provider | Strategy type | Asset class | Period | Real vs demo | Return | Max drawdown | Tier | Source |
|---|---|---|---|---|---|---|---|---|---|
| Waka Waka EA, account "MischenkoValeria" (#8379251) | Valery Trading (vendor); account run by a user | Grid EA | FX (MT4) | Started 4 Jun 2018; snapshot c. mid-2026 | Real (USD) | Myfxbook "Gain" +12,335%; **absolute gain +467%** (deposits $3,500, withdrawals $4,352, balance $15,503) | 66.54% | A (Myfxbook-tracked real account; I did not re-check the badge live) | [Oreshnikbot analysis](https://oreshnikbot.com/waka-waka-ea-myfxbook-analysis/); [MyFxBots review](https://www.myfxbots.com/reviews/forex-robots/waka-waka/); [Myfxbook page](https://www.myfxbook.com/members/MischenkoValeria/waka-waka-ea/8379251) |
| Waka Waka EA, account "SopmodBlock" | same EA, user account | Grid EA | FX | Dec 2021 – Feb 2022 (last updated Jun 2022) | Real | Rose about +400% to a $6,021 peak on 11 Feb 2022, then collapsed between 9 and 11 Feb 2022: Gain −92.05%, absolute gain −64.66%, balance $0 | 98.69% | A | [Oreshnikbot](https://oreshnikbot.com/waka-waka-ea-myfxbook-analysis/) |
| Waka Waka vendor account #12286158 | Valery Trading | Grid EA | FX | Since Oct 2020 | Stated real | not captured | 23.84% (vendor-stated) | D/E (vendor marketing) | [Valery Trading product page](https://www.valerytrading.com/products/waka-waka) |
| Waka Waka, other user accounts | users | Grid | FX | 2023– | Real | e.g. "4ndr345" (EUR): +80.27% gain / +69.53% absolute since May 2023 | 35.24% for 4ndr345. Other user accounts show max drawdowns of 43.95%, 23.76% and 84.71%; I did not re-verify which figure belongs to which account | A | [Oreshnikbot](https://oreshnikbot.com/waka-waka-ea-myfxbook-analysis/); Myfxbook pages: [KadenHeathcote](https://www.myfxbook.com/members/KadenHeathcote/wakawakaea/10366395), [rjriley](https://www.myfxbook.com/members/rjriley/waka-waka-ea/10637032), [tarek2750](https://www.myfxbook.com/members/tarek2750/waka-waka-ea/10105607) |
| Night Hawk EA | developer (MQL5 blog) | not stated | FX | "since 2019" | Claims a real IC Markets account | not given | not given | E (developer's own blog; no figures) | [MQL5 blog](https://www.mql5.com/en/blogs/post/775039) |
| "Techno Long Term" MQL5 signal | MQL5 provider (apparently the same "Techno" family the Oct 2026 survivorship blog author closed other signals from; not confirmed) | not stated | FX | Live since 2024 (93 weeks) | Not confirmed in my source | Growth +635% since 2024 | not captured | A (MQL5 broker-linked), but under 2 years | [MQL5 signal 2307342](https://www.mql5.com/en/signals/2307342) |
| Thomas Parry Jones (eToro Popular Investor) | eToro PI | not captured | Multi-asset (eToro) | 2024 – 2026 YTD | Real (eToro broker records) | 2024 +31.87%; 2025 +50.52%; **2026 YTD −33.43%** | not captured | B | [eToro profile](https://www.etoro.com/people/thomaspj) |
| Kevin Davey, World Cup entries | KJ Trading Systems | Systematic/algorithmic futures | Futures | 2005, 2006, 2007 contest years | Real money ($15,000 account) | 2005: 148.0% (2nd); 2006: 106.7% (1st); 2007: 111.6% (2nd) | not published | A (organizer standings, via a secondary site that says it has not audited statements) | [Complete Trader's Edge](https://completetradersedge.com/?p=235275); [MoneyShow bio](https://www.moneyshow.com/expert/508BF92DC707479EABECA781B61D769C) |
| Andrea Unger, World Cup entries | Unger Academy | (systematic; not detailed in sources) | Futures (2010 entry listed as combined futures and forex) | 2008, 2009, 2010, 2012 titles | Real money | 2008: 672%; 2009: 115%; 2010: 240%; 2012: not captured | not published | A (via secondary listings) | [Trading-Tournaments hall of fame](https://trading-tournaments.com/hall-of-fame) |
| Larry Williams, 1987 World Cup | — | Discretionary/technical futures | Futures | 1987 | Real money ($10,000) | 11,376% ($1,137,600 profit) | Self-reported equity path: about $2.2M down to $750,000, ending about $1.1M | A for the return; D for the drawdown | [CTE Larry Williams page](https://completetradersedge.com/larry-williams-11376-percent-trading-record/); [Benzinga interview](https://feeds2.benzinga.com/markets/futures/10/06/321532/making-millions-with-commodities-benzinga-s-exclusive-interview-with-la) |
| Trade Ideas "Holly" simulated portfolio | Trade Ideas | AI-selected intraday equity strategies, no overnight holds | US/Canadian equities | Calendar 2017 (inception 4 Jan 2016) | **Simulated paper trades** ("It is not a backtest"); slippage not modeled | +56% net (Risk-On; 85% gross); +41% Risk-Off; SPY +21.7%; 3,686 trades, 54.3% winners, PF 1.37, Sharpe 3.65 | not given | E (company-reported simulation) | [Trade Ideas press release, Jan 2018](https://www.prweb.com/releases/2018/01/prweb15071895.htm) |
| Tickeron AI robots | Tickeron | Various AI "robots" and agents | Equities, leveraged ETFs, crypto | 2025–2026 | Mixed: robot pages are served under "papertrades"; releases say "historical backtested or platform-reported" | e.g. "+159% annualized... 90% win rates" (Dec 2025 release) | not given | E | [Tickeron release](https://tickeron.com/trading-investing-101/tickerons-ai-trading-robots-deliver-159-returns-with-90-win-rates-on-leveraged-etfs/); [robot paper-trades page](https://tickeron.com/app/mobilewebviewpapertrades/ai-robot/4893/); [press release on labeling](https://www.wboc.com/online_features/press_releases/tickeron-highlights-ai-trading-agent-performance-across-multiple-market-sectors/article_49b9154d-1dfc-5d43-96cd-06218ad853ed.html) |

**Notable blow-ups and reversals of previously "verified" performers**
- **Waka Waka "SopmodBlock" (Feb 2022).** A real Myfxbook account on a grid EA rose about +400% and then lost almost everything in about 2 days (98.69% drawdown) — [Oreshnikbot](https://oreshnikbot.com/waka-waka-ea-myfxbook-analysis/)
- **Collective2 volatility strategies (Feb 2018 "Volmageddon").** Popular C2 strategies that were short volatility "blew up", and about $30M of roughly $100M AUM left the platform — [C2 blog](https://trade.collective2.com/boring-trading-strategies-nice-during-crazy-times). For context, inverse-VIX products including XIV took losses large enough that Credit Suisse terminated XIV — [PRWeb volatility advisor release](https://www.prweb.com/releases/vix_spike_and_xiv_termination_invest_in_vol_the_volatility_advisor_explains/prweb15187114.htm)
- **Bybit "Gold" leaders (2022–2023).** Most promoted Gold portfolios collapsed about six days after promotion, and the bottom quartile cost copiers more than USD 15,000 within 10 days. A TraderWagon leader featured on the front page in Feb 2023 then had "most... portfolios closed quickly with losses thereafter" — [Kawai et al.](https://www.andrew.cmu.edu/user/nicolasc/publications/Kawai-CHI24.pdf)
- **3Commas API-key leak (Oct–Dec 2022).** Bot users' exchange accounts were drained through leaked or phished API keys; details in Q1 — [Cointelegraph](https://cointelegraph.com/news/3commas-ceo-confirms-api-key-leak-following-warning-from-cz)
- **Mirror Trading International (Steynberg).** The "AI bot" track record was fake balances in MetaTrader demo accounts; more than $1.7B in BTC was taken from at least 23,000 people — [CFTC advisory](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html)
- **LUNA collapse (May 2022).** LUNA fell 97% in 24 hours — [Fortune, 11 May 2022](https://fortune.com/2022/05/11/luna-ust-reddit-stablecoins-crypto-crash/). I found no documented loss figures for exchange grid bots (Pionex, KuCoin) specifically.
- **eToro PI Thomas Parry Jones.** After +31.87% (2024) and +50.52% (2025), the profile shows −33.43% for 2026 YTD — [eToro profile](https://www.etoro.com/people/thomaspj)

### Inferences
- **Waka Waka annualized returns (my arithmetic; snapshot date about mid-2026, so roughly 8 years).** The "MischenkoValeria" account shows the Gain-vs-absolute-gain distortion:
  - Myfxbook's chain-linked "Gain" of +12,335% works out to about 83% a year.
  - Money actually made on deposits (+467%) works out to about 24% a year.
  - The account went through a drawdown of about two-thirds.
- **One surviving account is not evidence that a robot works.** The same commercial grid EA produced an 8-year survivor and a wipe-out within 2 months, depending on settings, capitalization and start date. Hundreds of user accounts exist, so the best one is what gets shown.
- Platforms with real records (eToro, Darwinex, exchange data) show strong multi-year runs followed by sharp reversals. Combined with Q2's lack of persistence, a 2–3 year record of 30–50% a year is weak evidence of a durable edge unless the drawdown profile and strategy logic are understood.
- **The only systematic traders with public, real-money, third-party-recorded results I found are contest entrants (Davey, Unger).** Their records are one-year windows built to maximize return, not multi-year audited compounding records; see Q5.

### Gaps
- **Darwinex long-running DARWINs:** I could not retrieve the Hall of Fame page (redirect loop), so I have no specific multi-year DARWIN names, returns or drawdowns.
- **Long-running EAs and providers on Myfxbook and MQL5:** apart from Waka Waka, I found no named EA or provider with a verified 5+ year real-money record and full metrics. The Night Hawk "since 2019" claim has no figures.
- **Collective2 15-year strategies:** I found no specific long-lived strategies with numbers. Klein says some exist, but they are hypothetical-fill records.
- **Copy-trader blow-ups:** I found no well-sourced, named case of an eToro Popular Investor, ZuluTrade provider or Binance/Bybit/Bitget lead trader wiping out copiers, beyond the aggregate Bybit Gold-leader finding.
- **Andrea Unger:** his 2012 return was not captured, and a promotional claim of "zero losing months" in 2023–2025 on Robbins' platform is unverified (E).

---

## 4. Retail stock/options bot and AI-signal products: are their results live or simulated, and is any of it independently verified?

### Takeaway
None of the retail AI and bot products I checked publish independently verified live-money track records:
- **Trade Ideas** publishes simulated paper-trade results for "Holly", without slippage.
- **Tickeron** mixes backtested, virtual paper-trading and "platform-reported" figures.
- **Composer** shows each user their own live results next to backtests, but publishes no audited aggregate.
- **Surmount, Option Alpha and Capitalise.ai:** I found no verified live data at all.

### Cited Findings
- **Trade Ideas (Holly AI)** — [PRWeb, Jan 2018](https://www.prweb.com/releases/2018/01/prweb15071895.htm)
  - Its 2017 results are described as a "simulated long/short equity portfolio" reflecting "historical daily paper trades in the U.S. and Canadian equity markets. It is not a backtest."
  - Slippage is not modeled; commissions are assumed at $0.0075 per share; short trades assume borrow is available; no overnight holds.
  - Returns: +56% net (Risk-On), 85% gross, +41% Risk-Off, against SPY +21.7%. The company claims the record is "free from selection or survivorship bias", with no third-party verification.
- **Trade Ideas, third-party review (unverified sourcing)** — [TradeAlgo review](https://www.tradealgo.com/trading-guides/ai-trading/trade-ideas-review)
  - Puts Holly's published 2025 performance at about 25% a year with a 62% win rate.
  - Estimates that real-world slippage on volatile small caps can cut returns by 20–40%.
- **Tickeron**
  - A release says figures are "historical backtested or platform-reported strategy performance, depending on the individual Trading Agent" — [Tickeron press release via WBOC](https://www.wboc.com/online_features/press_releases/tickeron-highlights-ai-trading-agent-performance-across-multiple-market-sectors/article_49b9154d-1dfc-5d43-96cd-06218ad853ed.html)
  - Robot performance pages are served under a "papertrades" path — [example robot page](https://tickeron.com/app/mobilewebviewpapertrades/ai-robot/4893/)
  - Headline claims include "+159% annualized... with 90% win rates" (Dec 2025) and "up to 171% annualized returns in live trading" — [Tickeron +159%](https://tickeron.com/trading-investing-101/tickerons-ai-trading-robots-deliver-159-returns-with-90-win-rates-on-leveraged-etfs/); [Tickeron 171%](https://tickeron.com/trading-investing-101/ai-trading-agents-deliver-up-to-171-annualized-returns-in-live-trading/)
  - A Sept 2025 release reports 37 of 40 trades closed profitably, a very small sample — [Tickeron Sept 2025](https://tickeron.com/trading-investing-101/ai-trading-robots-deliver-stellar-performance-90-profitable-trades-since-september-1-2025/)
- **Composer**
  - Its help center says backtests simulate "how a trading strategy, called a 'symphony,' might have performed in the past". It also notes that live decisions use real quotes during the trading window, while backtest prices do not — [Composer help: Backtest basics](https://help.composer.trade/article/67-backtest-basics)
  - Composer now overlays a symphony's backtest on its live performance for each user — [Composer What's New](https://www.composer.trade/whats-new)
  - A third-party 30-day live test found results roughly flat after fees, against a 10-year backtest of about 11.4% a year with a −21% maximum drawdown — [AlphaGainDaily review](https://alphagaindaily.com/en/blog/composer-ai-trading-review)
- **CFTC warning (Jan 2024)** — [CFTC advisory](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html)
  - "Scammers claim [AI]-created algorithms can generate huge returns... these promises were false." Also: "[AI] technology can't predict the future or sudden market changes."

### Inferences
- **Paper-trade logs are better than backtests but are not live records.** Trade Ideas' paper-trade log is forward-generated, which removes look-ahead bias, so it is better than a backtest. It still ignores slippage and fill problems, which are largest exactly where intraday small-cap AI signals trade. Per the tier system it is E (company-reported simulation), not A or B.
- **Tickeron's headline numbers cannot be treated as live returns.** The labeling is inconsistent and the robot pages are paper trades. Very high win rates (about 90%) on small samples, such as 37 of 40 trades, fit small-sample luck or payoff profiles that win often and lose big, but do not prove either. This is my inference, not shown for Tickeron.
- **For any of these products to count as "real forward results",** a user would need broker statements or a broker-linked tracker covering at least a year, with fees. None of the vendors offers this as a published, third-party-audited record.

### Gaps
- I found no sources on live versus backtested results for Surmount, Option Alpha (bots) or Capitalise.ai, and no evidence that any of them publishes verified live track records.
- I did not locate Trade Ideas' current (2024–2026) official Holly performance page or its exact disclaimer wording. The 2025 figures come from a third-party review.
- I found no independent audit (for example GIPS or a third-party verifier) of any retail AI signal product.

---

## 5. Real-money trading competitions: how they are verified and whether winners keep winning

### Takeaway
The Robbins World Cup Championship and the U.S. Investing Championship use real-money accounts and publish standings. They are among the few public, broker-recorded results for systematic traders: Kevin Davey's algorithmic futures finished in the top two three years running, and Andrea Unger won three straight titles plus a fourth. However:
- They are one-year, return-maximizing contests.
- The World Cup ranks only an entrant's best account and does not publish its field size.
- Winners' later multi-year results are rarely published.

So the contests show that persistence can exist among a few people, but they do not establish base rates.

### Cited Findings
- **World Cup rules.** Minimum accounts are $10,000 for futures and $5,000 for forex, with at least 10 round-turn trades — [Finance Magnates](https://www.financemagnates.com/thought-leadership/robbins-world-cup-trading-championship-expands-japan/); [NexusFi](https://nexusfi.com/d/education/world-cup-trading-championships/). An older entry form says a $15,000 minimum per entry — [x-trader.net form](https://x-trader.net/foro/download/file.php?id=23862)
- **World Cup vs U.S. Investing Championship (per a secondary comparison site, reviewed Sept 2026)** — [Complete Trader's Edge: WCTC vs USIC](https://completetradersedge.com/?p=235280)
  - The World Cup is run through "Authorised brokers introduced by the organiser" and scores net return on total funds deposited.
  - The World Cup "allows several accounts and ranks only the best".
  - The U.S. Investing Championship uses "One real-money account, selected before tracking begins", with a $20,000 minimum.
  - Neither contest describes an independent audit.
  - The World Cup does not publish its field size. U.S. Investing entrants grew from 124 (2020) to 579 (2025).
  - The site reports regulatory history (a 2003 Robbins CFTC settlement with a $120,000 penalty, and a Zadeh SEC order with a $165,000 FINRA penalty), adding that these do not concern whether contest results were accurate.
- **Median winning returns** — [CTE](https://completetradersedge.com/?p=235275); [CTE comparison](https://completetradersedge.com/?p=235280)
  - The median annual World Cup futures champion since 1984 made 251.8%.
  - 2020–2025 medians: 333.5% for the World Cup futures champion; 627.1% for the U.S. Investing $20k+ stock champion.
- **Kevin Davey (systematic futures)** — [CTE Davey page](https://completetradersedge.com/?p=235275); [MoneyShow](https://www.moneyshow.com/expert/508BF92DC707479EABECA781B61D769C)
  - Results: 2005, 2nd with 148.0% (winner Ed Twardus, 278.0%); 2006, 1st with 106.7%; 2007, 2nd with 111.6% (winner Michael Cook, 249.7%).
  - He used a $15,000 account and targeted about 100% a year, a figure he got from asking the broker for past top-three finishes.
  - The site says it has not audited statements, and it flags that KJ Trading's "three-time winner" marketing overstates the official record (one win).
- **Andrea Unger** — [Trading-Tournaments](https://trading-tournaments.com/hall-of-fame)
  - Champion in 2008 (672%), 2009 (115%) and 2010 (240%), plus a fourth title in 2012. He is called the only four-time champion.
- **Larry Williams (1987)**
  - Return of 11,376% on $10,000, which has stood as the record for nearly 40 years — [CTE](https://completetradersedge.com/larry-williams-11376-percent-trading-record/)
  - He says in interview the account reached $2.2M, fell to $750,000, and ended about $1.1M — [Benzinga](https://feeds2.benzinga.com/markets/futures/10/06/321532/making-millions-with-commodities-benzinga-s-exclusive-interview-with-la)
  - Forum posts quoting NFA material allege that his *managed* accounts lost heavily in 1987 (one figure: −$6,122,281 across accounts against +$902,599 on the contest account) and that he and Robbins Trading were fined. These figures are unverified and conflict with the $1.137M profit figure — [EliteTrader thread](https://www.elitetrader.com/et/threads/larry-williams.379087/post-5953152)
  - Michelle Williams (his daughter) won in 1997 with about 1,000% — [CTE](https://completetradersedge.com/larry-williams-11376-percent-trading-record/)
- **Recent winners (sources conflict)**
  - Ivan Scherman, 2023 futures: 491.4% — [Quantamental Trader Substack](https://quantamentaltrader.substack.com/p/world-cup-trading-championship-and)
  - Serghey Magala, 2023: 280.5% futures and 355.3% forex — [Substack](https://quantamentaltrader.substack.com/p/world-cup-trading-championship-and). A different site lists Magala as back-to-back forex champion in 2023 (355.30%) and 2024 (201.00%) — [Trading-Tournaments](https://trading-tournaments.com/hall-of-fame)
  - The Substack names Gianluigi Ventre as 2024 forex champion with "over 100%" and Ryan Michael LaVelle as 2024 futures champion with 138.6%.
- **Repeat performers** — [CTE comparison](https://completetradersedge.com/?p=235280)
  - Sean Ryan had seven profitable U.S. Investing entries in seven years.
  - Law Wai-Sum won back-to-back $1M+ stock titles in 2024 and 2025.
  - Michael Cook's World Cup titles (2007, 2014) and U.S. Investing second places (2022, 2023) are not confirmed to be the same person.

### Inferences
- **What the contests verify, and the selection problem.** They verify that real money was traded at a real broker, which is stronger than Myfxbook or MQL5 for that one year. But:
  - Allowing multiple accounts and ranking only the best (World Cup) adds the same selection bias seen on copy-trading platforms.
  - Without the field size, a winner's return cannot be turned into a luck-adjusted significance level.
- **Winning requires extreme risk.** Median winning returns of 250–630% mean winners use aggressive leverage; Larry Williams's own account showed a roughly two-thirds intra-year drawdown (my arithmetic from his figures). These results say little about the risk-adjusted, multi-year performance a bot buyer cares about.
- **Persistence evidence is real but anecdotal.** Davey had three straight podiums with a pre-set ~100% target using systematic futures; Unger won three straight titles. Both later built education and course businesses, and neither has a published multi-year audited record in the sources I found.

### Gaps
- I found no official Robbins (worldcupchampionships.com / worldcupadvisor) rules page describing how statements are verified, and no official archive page. All World Cup figures above come from secondary sites that say they drew on organizer standings.
- I found no data on what fraction of World Cup or U.S. Investing entrants lose money, or on winners' results in later years (for example, a winner's following-year return).
- I could not verify the NFA findings about Larry Williams's 1987 managed accounts from a primary NFA or CFTC document.
- Sources conflict on the 2024 forex champion (Magala at 201% vs Ventre at "over 100%") and on Magala's 2023 futures figure.
