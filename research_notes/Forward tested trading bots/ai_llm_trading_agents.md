# AI- and LLM-Driven Trading Agents, Bots and Funds with Real Forward-Tested Results (research as of 2026-11-23)

Verification tiers used throughout (from the assignment): **(A)** third-party/broker-linked or on-chain verified; **(B)** regulated fund/ETF public NAV; **(C)** peer-reviewed or preprint out-of-sample study; **(D)** self-reported with statements or logs; **(E)** self-reported marketing claim only. "My calculation" marks arithmetic I derived from cited figures, not a figure printed by the source.

---

## 1. Alpha Arena by Nof1 (Season 1 crypto perps, Season 1.5 US stocks, any 2026 season)

### Takeaway
Alpha Arena is the best-verified real-money LLM trading test to date: its wallets are public on Hyperliquid, and a third party recomputed the results from on-chain fills. The results are overwhelmingly negative. Across Seasons 1 and 1.5, 31 of 38 accounts of $10K each lost money, the pooled $380K lost about 27%, and about $43K went to fees. Each season's winner came from a single ~2-week run with no persistence across seasons: Qwen3 Max won Season 1 with about +20–22%, and the "Mystery Model" (Grok 4.20) won Season 1.5 with about +12–13%. These wins are indistinguishable from luck. As of Nov 2026, no Season 2 has launched.

### Cited Findings

**Season 1 setup (crypto perpetuals, real money)**
- **Dates:** Oct 17/18 – Nov 3, 2025. Sources differ on the start: Oct 17 per [TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/), Oct 18 per [TradeRank](https://www.traderank.ai/alpha-arena-leaderboard). Nof1's writeup says the season ended Nov 3, 2025, 5:00 p.m. ET ([Moby summary of Nof1 post](https://moby.win/learn/alpha-arena/)).
- **Capital and models:** six models with $10,000 each (≈$60K real money) on Hyperliquid perps: Qwen3 Max, DeepSeek Chat V3.1, Claude Sonnet 4.5, Grok 4, Gemini 2.5 Pro and GPT-5 ([TradeRank](https://www.traderank.ai/alpha-arena-leaderboard); [SCMP](https://www.scmp.com/tech/tech-trends/article/3331425/alibabas-ai-model-outperforms-us-rivals-crypto-trading-showdown)).
- **Rules and inputs** (Nof1's writeup "Exploring the Limits of Large Language Models as Quant Traders", 27 Oct 2025, at https://www.alphaarena.ai/blog/TechPost1, as summarized by Moby; direct fetch was rate-limited) ([Moby](https://moby.win/learn/alpha-arena/)):
  - Assets: BTC, ETH, SOL, BNB, DOGE and XRP perps.
  - All models shared one system prompt, one user-prompt template and the same numeric data. No news and no fine-tuning.
  - About every 2–3 minutes, each model output long, short, hold or close, plus size, leverage, an exit plan and a 0–1 confidence score.
  - The goal was to maximize PnL.
- **Leverage caps conflict between secondary sources** (10–20×, 1–20×, or 25×). Upscale claims Qwen "often used 25× leverage on a single large position" while GPT-5 and Gemini averaged under 1× ([Upscale](https://upscale.trade/blog/ai-trading-alpha-arena)). The prompt text circulating on GitHub is a reverse-engineered reconstruction, not an official document ([gist](https://gist.github.com/patrickleehua/21ca475012e018824ca3c310546e483b)).
- **Nof1's own observations** ([Moby](https://moby.win/learn/alpha-arena/)):
  - Qwen3-Max used the largest sizes, had the highest confidence and ran 1–2 positions.
  - Gemini 2.5 Pro traded the most and shorted often.
  - Claude Sonnet 4.5 rarely shorted.
  - GPT-5 had the lowest confidence.
  - Highest confidence did *not* correspond to better trading.
  - Early pre-launch runs were "dominated by trading fees from frequent small gains", so the prompt was tightened.
  - The data had bugs: a newest-first price list was misread, and "free collateral" was confused with "available cash".
- **Nof1's own caveat:** do not name a permanent best model from one run, citing prompt bias, small samples, no statistical rigor, a short window and possible luck ([Moby](https://moby.win/learn/alpha-arena/)).
- **Close:** Founder Jay Azhang announced that "Qwen 3 MAX pulled ahead at the very end to secure the win" ([X post](https://x.com/jay_azhang/status/1985481491078328621)).

**Season 1 results: three versions of the "final" numbers**

| Model | Press/Nof1 close numbers ([iWeaver](https://www.iweaver.ai/blog/alpha-arena-ai-trading-season-1-results/), [Briefs](https://www.briefs.co/news/qwen3-max-tops-alpha-arena-season-1-most-models-lost-money/)) | nof1.ai figures read Aug 6, 2026 ([TradeRank](https://www.traderank.ai/alpha-arena-leaderboard)) | On-chain recompute ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)) | PnL | Fees | Fills | Realized max DD | Hyperliquid address |
|---|---|---|---|---|---|---|---|---|
| Qwen3 Max | +22.31% | $12,231 (+22.31%) | **+20.3%** | +$2,035 | $1,669 | 456 | −45.2% | 0x7a8fd8bba33e37361ca6b0cb4518a44681bad2f3 |
| DeepSeek Chat V3.1 | +4.89% | $10,489 (+4.89%) | **+6.9%** | +$685 | $719 | 341 | −55.4% | 0xc20ac4dc4188660cbf555448af52694ca62b0734 |
| Claude Sonnet 4.5 | −30.81% | $5,799 (−42.01%) | **−29.9%** | −$2,994 | $590 | 320 | −43.0% | 0x59fa085d106541a834017b97060bcbbb0aa82869 |
| Grok 4 | −45.3% | $4,208 (−57.92%) | **−45.1%** | −$4,514 | $391 | 346 | −53.0% | 0x56d652e62998251b56c8398fb11fcfe464c08f84 |
| Gemini 2.5 Pro | −56.71% | $5,445 (−45.55%) | **−57.7%** | −$5,766 | $1,347 | 1,286 | −75.6% | 0x1b7a7d099a670256207a30dd0ae13d35f278010f |
| GPT-5 | −62.66% | $4,126 (−58.74%) | **−63.4%** | −$6,341 | $545 | 684 | −76.0% | 0x67293d914eafb26878534571add81f6bd2d9fe06 |

- **Recompute method:** TradingAgentStack computed PnL as realized PnL − fees + funding from Hyperliquid fills, with open positions marked on 4-hour candles. It says this can move results by "a point or two". Its drawdown is realized-only, so it is a floor. Wallet addresses were taken from archived nof1.ai pages, with "no separate verification of ownership" ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)).
- **Source caveats:** TradingAgentStack and TradeRank are commercial sites with affiliate links or a competing arena. Mainstream coverage confirms the headline Qwen +22% in ~2 weeks ([SCMP](https://www.scmp.com/tech/tech-trends/article/3331425/alibabas-ai-model-outperforms-us-rivals-crypto-trading-showdown)).

**Season 1.5 (US stock perps + crypto, real money)**
- **Dates and venue:** Nov 19 – Dec 3, 2025, on Hyperliquid, including HIP-3 US-stock perps ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)). Tickers included TSLA, NVDA, MSFT, AMZN, GOOGL, PLTR and the Nasdaq-100 ([TradeRank](https://www.traderank.ai/alpha-arena-leaderboard)).
- **Structure:** eight models, each running four accounts under different rule sets: "Monk Mode", "New Baseline", "Max Leverage" and "Situational Awareness". That makes 32 accounts × $10K = $320K ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)).
- **Official result:** the "Mystery Model", revealed as Grok 4.20, won with **+12.11% aggregate, $4,844 profit** across its four entries ([TradeRank](https://www.traderank.ai/alpha-arena-leaderboard); [GNcrypto](https://www.gncrypto.news/news/mystery-model-alpha-arena-season-1-5-winner/)). TradeRank notes that per-competition rows on nof1's longer-window board "do not reconcile with the announced figure".
- **On-chain recompute** (four accounts per model, $40K each) ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)):

| Model | Return | PnL | Fees | Best rule set | Worst rule set |
|---|---|---|---|---|---|
| Grok 4.20 (Mystery) | **+13.0%** | +$5,206 | $1,514 | Situational Awareness +33.7% | Monk −0.8% |
| GPT-5.1 | −6.0% | −$2,394 | $3,133 | Max Leverage +18.8% | New Baseline −20.4% |
| Qwen3 Max | −29.7% | −$11,793 | $6,209 | Monk −1.8% | Situational Awareness −69.3% |
| Gemini 3 Pro | −30.1% | −$12,048 | $4,463 | Monk −0.6% | New Baseline −45.1% |
| DeepSeek Chat V3.1 | −32.9% | −$13,169 | $6,091 | Monk +16.7% | Max Leverage −64.6% |
| Kimi K2 Thinking | −34.2% | −$13,674 | $6,171 | Monk −19.5% | New Baseline −51.8% |
| Claude Sonnet 4.5 | −39.1% | −$15,589 | $4,845 | Monk −13.3% | Situational Awareness −58.5% |
| Grok 4 | −58.7% | −$23,431 | $5,248 | New Baseline −36.9% | Situational Awareness −93.4% |

- **Rule-set totals:** Monk −9.5% (1/8 accounts up), New Baseline −28.6% (1/8), Max Leverage −28.8% (2/8), Situational Awareness −41.8% (1/8). Overall 5 of 32 accounts were up and 7 of 8 models lost money. Situational Awareness accounts made roughly 7,900–11,700 fills each, except Grok 4.20's 1,613 ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)).
- **Runners-up:** secondary reports say Nof1 placed GPT-5.1 2nd and Gemini 3 3rd ([GNcrypto](https://www.gncrypto.news/news/mystery-model-alpha-arena-season-1-5-winner/)). The on-chain recompute puts Gemini 3 Pro 4th, 0.4 pp behind Qwen3 Max ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)).
- **Both seasons combined:** "31 of 38 accounts lost money"; accounts "paid $43k in fees on $380k of stakes" ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)).

**Mainstream critique**
- Bloomberg (Justina Lee, May 6, 2026) wrote that AI models in public trading contests "mostly lose money". In the eight-model, four-competition contest the portfolio "as a whole lost about a third of its capital", and a model finished in profit "only six times" out of 32 ([Bloomberg via Tribune syndication](https://www.dailygazette.com/tribune/ai-bots-auditioning-for-wall-street-trading-are-mostly-losing/article_c6fd5b03-c02a-5382-a3b2-ce63716dc754.html); [summary on X](https://x.com/cfromhertz/status/2052001782197293396)). Note the discrepancy with the on-chain recompute: 5 of 32 profitable, −27% overall.
- The same article says models trade too frequently and "make wildly different decisions when given identical instructions", and that the contests are "far from academically rigorous" ([X summary](https://x.com/cfromhertz/status/2052001782197293396)).
- ThinkAdvisor's version (May 6, 2026) adds that a hedge-fund head of data science wrote that no AI trading bot he tracks has shown a lasting edge. An unnamed expert said "most public experiments are still too short and too noisy to support firm conclusions" ([ThinkAdvisor](https://www.thinkadvisor.com/amp/2026/05/06/why-ai-bots-arent-ready-to-replace-your-fund-manager/)).
- Commentary attributes the S1 losers' results to overtrading and the leaders' drawdowns to excessive leverage ([Upscale](https://upscale.trade/blog/ai-trading-alpha-arena)). Mid-season coverage tracked the swings ([Decrypt](https://decrypt.co/345006/ai-crypto-trading-showdown-deepseek-grok-winning-gemini-implodes?amp=1)). A claim that buy-and-hold beat most AIs in week 1 appeared in search results, but I could not pin down its source (see Gaps).

**Season 2 / 2026 status**
- As of Nov 12, 2026, alphaarena.ai still shows Season 1.5 with a banner saying the models are no longer running. No Season 2 roster, results or leaderboard has been published ([TradeRank](https://www.traderank.ai/alpha-arena-leaderboard)).
- TradingAgentStack lists Season 2 as "Not launched as of Oct 2026". It reports that Nof1 raised $15M in May 2026 and plans to run Season 2 ([TradingAgentStack](https://tradingagentstack.com/alpha-arena-results/)).
- BigGo reports planned Season 2 features: web search, longer thinking time, more data sources and multi-step execution ([BigGo](https://finance.biggo.com/news/5BSX_Z0BaoGGrU-ID27J)).
- Upscale's claim that a "second season, on US stocks" had a different winner appears to conflate it with Season 1.5 ([Upscale](https://upscale.trade/blog/ai-trading-alpha-arena)).

**Verification tier: A.** Public Hyperliquid wallets were independently recomputed. Residual uncertainties: wallet attribution relies on Nof1's own pages, and results depend on the mark-to-market timestamp.

### Inferences
- **Pooled performance (my calculation from TradingAgentStack PnL):**
  - Season 1: −$16,895 on $60,000 = **−28.2%**.
  - Season 1.5: −$86,892 on $320,000 = **−27.2%**.
  - Combined: −$103,787 on $380,000 = **−27.3%** over ~4 weeks of live trading.
  - Fees: $5,261 in S1 (8.8% of capital in ~17 days) and $37,674 in S1.5 (11.8% in 2 weeks). Together that is ≈$42.9K, about **41% of all losses**, consistent with the "$43k" stated by the source.
- **Overtrading is visible in the data (my calculation).** S1.5 Situational Awareness accounts paid ≈$17,438 in fees on $80K, about 21.8% of capital, roughly half of that mode's −41.8% loss. Monk Mode paid ≈$4,904 (6.1%) and had the smallest loss (−9.5%).
- **No persistence between seasons, which suggests luck rather than skill.** S1 winner Qwen3 Max lost in all four S1.5 rule sets (−29.7% aggregate). S1 runner-up DeepSeek went from +6.9% to −32.9%. The S1.5 winner (Grok 4.20) did not compete in S1.
- **Prompt variation mattered as much as model choice.** Within a single model, S1.5 rule sets ranged from +16.7% to −64.6% (DeepSeek) and from +18.8% to −20.4% (GPT-5.1). That spread is as large as the spread between models, so model "rankings" from one prompt and one 2-week window are mostly noise.
- **Statistical power is very low.** S1 was ~6 correlated bets on the same six crypto assets over ~17 days with leverage. Qwen's realized drawdown (−45%) was twice its final gain. No benchmark-relative or significance analysis was published.
- **Practical reading for the user:** the only tier-A LLM trading evidence says that frontier LLMs, prompted to trade autonomously at high frequency with leverage, lose money on average, mostly through fees and risk-taking. Positive single-run results should be expected by chance in a 38-account field.

### Gaps
- I could not find a Nof1-published final BTC (S1) or NDX/QQQ (S1.5) buy-and-hold comparison. A search-result claim that "a simple buy-and-hold strategy still outperformed most AIs" in week 1 of S1 could not be traced to a specific article. Attempts to pull price data to compute one myself were blocked. So no benchmark return for the same windows is given here.
- I could not obtain the official definitions of the four S1.5 rule sets, or the official leverage caps (secondary sources conflict).
- I could not fetch Nof1's blog directly (HTTP 404/429), so its content comes via Moby's summary.
- The press "final" numbers (e.g., Claude −30.81% vs −42.01%) differ by snapshot time. The on-chain recompute matches the Nov 3 press set within ~1–2 pp.
- The $15M raise and Season 2 plans are reported only by secondary sites. No Season 2 results exist as of the latest checks (Oct–Nov 2026).

---

## 2. Other live / forward LLM trading benchmarks and arenas (2024–2026)

### Takeaway
Academic "live" benchmarks from 2025 (LiveTradeBench, AI-Trader, Agent Market Arena) are genuinely forward in time. They are also short (5 weeks to ~2.5 months), mostly paper-traded and single-run. Results are mostly explained by market beta, with no consistent edge over buy-and-hold: no agent beat TSLA buy-and-hold in AMA, and 0/6 beat the SSE-50 in AI-Trader. General LLM capability does not predict trading results (LMArena-vs-return Spearman ≈ 0.05). Broader long-horizon tests (FINSABER) show earlier LLM "alpha" deteriorating. Commercial arenas (Rallies.ai) report big paper wins for single models, which is classic winner-picking among many entrants.

### Cited Findings

**Summary table**

| Benchmark | Who | Window (forward?) | Assets | Real vs paper | Headline result vs benchmark | Tier |
|---|---|---|---|---|---|---|
| LiveTradeBench | UIUC (Haofei Yu, Fenghai Li, Jiaxuan You) | Aug 18 – Oct 24, 2025, 50 trading days, live | 15 US stocks/ETFs + cash; 10 Polymarket markets | Capital and real-money status not stated | Stocks: best GPT-4.1 +6.25%, worst Gemini-2.5-Pro +1.95%. Polymarket: +20.54% to −57.62%. No B&H in text read | C |
| AI-Trader | Univ. of Hong Kong (Chao Huang group; HKUDS repo) | Oct 1 – Nov 7, 2025 (stocks); Nov 1–14, 2025 (crypto), live | Nasdaq-100 hourly; SSE-50 daily; 10 crypto pairs | Not stated | US: 3/6 beat QQQ (+1.87%). A-shares: 0/6 beat SSE-50 (+1.65%). Crypto: 1/6 beat CD5 (−14.30%) | C |
| Agent Market Arena (AMA) | The Fin AI + universities (incl. Lopez-Lira) | Aug 1 – Sep 30, 2025, live (warm-up May–Jul) | TSLA, BMRN, BTC, ETH | Paper | No agent beat TSLA B&H (+46.88%). Only one agent design beat ETH B&H (+18.56%) | C |
| StockBench | Tsinghua / BUPT | Mar 3 – Jun 30, 2025 (82 days); post-cutoff replay, not live | 20 largest DJIA stocks | Simulated | Equal-weight B&H +0.4%; best LLM ≈ +2.5%; "most… struggle to outperform" | C |
| FINSABER | Li, Kim, Cucuringu, Ma (KDD 2026 oral) | ~20-year backtest, 100+ symbols | US stocks | Simulated | Prior LLM advantages "deteriorate significantly" | C (backtest) |
| Rallies.ai AI Stock Market Arena | Rallies AI (commercial) | Late Nov 2025 → ongoing | US stocks | Paper, $100K per model | ChatGPT +72.4% vs S&P ≈ +11.3% (to ~Jun 21, 2026) | D |

**LiveTradeBench** ([arXiv 2511.03628](https://arxiv.org/html/2511.03628))
- 21 LLMs were evaluated live from Aug 18 to Oct 24, 2025 ("a total of 50 trading days") on U.S. stocks (15 equities/ETFs plus cash) and Polymarket (10 binary markets).
- **Best and worst results:**
  - Stocks, best by cumulative return: GPT-4.1, +6.25% (Sharpe 2.64, MDD 1.92%).
  - Stocks, worst: Gemini-2.5-Pro, +1.95% (Sharpe 0.61).
  - Polymarket, best: Claude-Sonnet-3.7, +20.54% (MDD 10.65%).
  - Polymarket, worst: Qwen3-235B-A22B-Thinking, −57.62% (MDD 72.10%).
  - Kimi-K2-Instruct: Sharpe −5.26, CR −53.44%.
- **LMArena correlation:** Spearman correlation between LMArena score and stock return was **0.054** ("virtually no relationship"), and **−0.38** on Polymarket. Heading: "High general LLM capability does not imply strong financial performance."
- **Motivation:** the authors say backtesting "is prone to information leakage". Starting capital and real vs paper were not stated in the portion I read.

**AI-Trader (HKUDS)** ([arXiv 2512.10971](https://arxiv.org/html/2512.10971v1))
- Six LLMs.

| Model | US CR (QQQ +1.87%) | US Sharpe | US MDD | A-share CR (SSE-50 +1.65%) | Crypto CR (CD5 −14.30%) |
|---|---|---|---|---|---|
| MiniMax-M2 | +9.56% | 4.42 | −4.92% | +1.31% | −14.80% |
| DeepSeek-v3.1 | +8.39% | 3.73 | −8.58% | −1.23% | **−12.18%** (only one to beat CD5) |
| Claude-3.7-Sonnet | +3.11% | 1.13 | −8.13% | +0.84% | −15.30% |
| GPT-5 | +1.56% | 0.70 | −10.55% | −3.53% | −16.41% |
| Qwen3-Max | +0.39% | 0.32 | −9.39% | −3.86% | −16.85% |
| Gemini-2.5-Flash | −0.06% | 0.09 | −7.73% | −1.53% | −18.63% |

- Paper conclusion: "general intelligence does not automatically translate to effective trading capability". Risk control, not return-chasing, drove MiniMax-M2's robustness. Generalization across markets is limited ([arXiv](https://arxiv.org/html/2512.10971v1)).
- The repo has ~22.2k GitHub stars ([star-history](https://www.star-history.com/hkuds/ai-trader/)).
- **Leaderboard snapshots differ from the paper.** A fork's leaderboard dated 2025-10-28 showed DeepSeek +14.38%, MiniMax-M2 +10.99%, GPT-5 +8.39% and QQQ +4.92% ([GitHub fork](https://github.com/leoayres/AI-Trader)). An undated snapshot showed DeepSeek +9.68%, Claude-3.7 +2.17%, GPT-5 +1.60% and QQQ +1.22% ([aibars](https://www.aibars.net/en/library/open-source-ai/details/770953972965052416)). Rankings and levels move a lot with the window chosen.

**Agent Market Arena (AMA)** ([arXiv 2510.11695](https://arxiv.org/html/2510.11695v1))
- Live paper trading Aug 1 – Sep 30, 2025.
- Agents: InvestorAgent, TradeAgent, HedgeFundAgent and DeepFundAgent, each on GPT-4o, GPT-4.1, Gemini-2.0-flash, Claude-3.5-haiku and Claude-sonnet-4, plus a majority-vote ensemble.
- **Buy-and-hold over the window:** TSLA +46.88% (Sharpe 6.00), BMRN −6.89%, BTC +0.66%, ETH +18.56%.
- **Best agents per asset:**
  - TSLA: InvestorAgent/GPT-4.1, +40.83% (higher Sharpe at 6.47 and lower MDD at 4.38%, but lower return than B&H).
  - BMRN: HedgeFundAgent, +23.70%.
  - BTC: TradeAgent/Gemini-2.0-flash, +5.02%.
  - ETH: HedgeFundAgent, +39.66%.
- **Other outcomes:** TradeAgent/GPT-4.1 lost −38.72% on TSLA.
- **Anomaly:** HedgeFundAgent's rows are identical across all five LLM backbones, which suggests a reporting or merging error ([arXiv](https://arxiv.org/html/2510.11695v1)).
- The paper calls the portfolio "simulated" and links a paper-trading page ([arXiv](https://arxiv.org/html/2510.11695v1)).

**StockBench** ([arXiv 2510.02209 v2](https://arxiv.org/html/2510.02209v2); [project site](https://stockbench.github.io/))
- Equal-weight buy-and-hold returned +0.4% (MDD −15.2%).
- Leaderboard: Kimi-K2 ranked #1 on a composite z-score with +1.9% return and −11.8% MDD; Qwen3-235B-Think had the highest return at about +2.5%.
- The authors say "most LLM agents struggle to outperform the simple buy-and-hold baseline". A secondary review counts 8 of 13 models above B&H on return, and all 13 with smaller drawdowns ([Quantex review](https://quantex.com.sg/research/2026-10-17-llm-agents-vs-buy-and-hold/)).
- It is a replay over a post-training-cutoff window (Mar 3 – Jun 30, 2025, 82 trading days, top-20 DJIA stocks), not live trading ([Quantex](https://quantex.com.sg/research/2026-10-17-llm-agents-vs-buy-and-hold/)).

**FINSABER** ([arXiv 2505.07078](https://arxiv.org/abs/2505.07078); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5287013))
- Two-decade backtests over 100+ symbols. Previously reported LLM advantages "deteriorate significantly" under a broader cross-section and longer evaluation.
- LLM strategies are "overly conservative in bull markets" (underperforming passive benchmarks) and "overly aggressive in bear markets" (heavy losses).
- The authors attribute earlier reported edges to survivorship and data-snooping biases.
- Venue: KDD 2026 Datasets & Benchmarks Track (oral). Current arXiv version v6 is dated Jun 26, 2026.

**AlphaForgeBench** ([arXiv 2602.18481](https://arxiv.org/pdf/2602.18481))
- Argues that single-run live evaluations are statistically unreliable because results depend on the execution window and LLM outputs vary across runs. It is itself a 2021–2026 backtest with no buy-and-hold comparison ([Quantex](https://quantex.com.sg/research/2026-10-17-llm-agents-vs-buy-and-hold/)).

**FinRL contests**
- The 2025 contest includes a FinRL-DeepSeek task (LLM-generated news signals for stock trading) and FinRL-AlphaSeek for crypto ([FinRL Contest 2025](https://open-finance-lab.github.io/FinRL_Contest_2025); [survey arXiv 2504.02281](https://arxiv.org/html/2504.02281v4)).
- Participation was 46, 21 and 85 teams in 2023–2025 ([survey](https://arxiv.org/html/2504.02281v4)).
- I found no published live or paper-trading-phase results.

**Rallies.ai AI Stock Market Arena** ([CryptoBriefing, Jun 21, 2026](https://cryptobriefing.com/chatgpt-leads-rallies-ai-stock-market-arena/))
- **Setup:** paper trading with no real money. Each model got $100K, starting late Nov 2025, on public stocks only. Rallies "publishes trade logs and portfolio holdings".
- **Results to ~Jun 21, 2026:** ChatGPT +72.4% ($100K → ~$172.4K) vs S&P 500 ≈ +11.3%. Grok and Claude were each "roughly 20–50%". Big winners were CRDO and NBIS, bought around Mar 2026.
- **Earlier snapshots:**
  - Early Jan 2026: DeepSeek v3 #1 at +4.6% among 8 AIs.
  - Jan 21, 2026: Grok 4 leading with +7% ([OneDayAdvisor](https://www.onedayadvisor.com/2026/01/AI-stock-trading-competition-Rallies.html); [ValueTheMarkets](https://www.valuethemarkets.com/cryptocurrency/news/ai-models-compete-in-stock-picking-contest-with-surprising-outcomes)).
- **Tier D:** the platform reports its own paper results, logs are public, and the operator has a commercial interest.

**Newer live-evaluation preprints (titles found, results not reviewed)**
- FIDES-Live ([arXiv 2610.36476](https://arxiv.org/pdf/2610.36476)), LiveOption ([arXiv 2609.33470](https://arxiv.org/pdf/2609.33470)) and LiveMACE ([arXiv 2610.09872](https://arxiv.org/pdf/2610.09872)).

**Popular GitHub "AI trader" repos generally have no forward record**
- **virattt/ai-hedge-fund** is described as a proof-of-concept "for educational and research purposes" with backtesting. Live trading is "disabled by default". Star counts are reported from ~45.6k to ~59.6k depending on snapshot ([Reskilll](https://blogs.reskilll.com/ai-hedge-fund-the-50k-star-open-source-multi-agent-investment-system/); [SourcePulse](https://www.sourcepulse.org/projects/1797841); [README](https://raw.githubusercontent.com/virattt/ai-hedge-fund/HEAD/README.md)).
- **TauricResearch/TradingAgents:** a third-party blog claims >80,000 stars (unverified) ([Pinggy](https://pinggy.io/blog/best_ai_trading_agents/)). I found no forward results.

### Inferences
- **Forward results mostly track market beta.**
  - In LiveTradeBench every model's stock return was positive (+1.95% to +6.25%) in a window when markets were rising, which suggests mostly long-beta exposure. No B&H baseline is shown to prove alpha.
  - In AMA, the strongest stock (TSLA +46.88%) was not beaten by any agent.
  - In AI-Trader, "wins" over QQQ were 1–8 points over 5 weeks, inside normal tracking error for concentrated hourly-traded portfolios, and they disappeared in A-shares.
- **No model family wins consistently.** DeepSeek was top-2 in AI-Trader US but negative in A-shares. Qwen3 Max won Alpha Arena S1 but finished 5th of 6 in AI-Trader US (+0.39%). Claude-3.7-Sonnet led LiveTradeBench Polymarket, yet Claude Sonnet 4.5 lost in both Alpha Arena seasons. This is consistent with noise, not a durable "best trading LLM".
- **Arena designs with many entrants guarantee a headline winner.** Rallies' ChatGPT +72.4% (paper, ~7 months, concentrated AI-infrastructure picks) is the best result among ~8 models. It needs to be judged against the dispersion of all entrants and the risk taken, not against the S&P alone.
- **Even the best-starred open-source "trading agent" repos lack timestamped forward records.** Among them, HKUDS/AI-Trader is the exception with a live paper benchmark, and its results are modest and inconsistent across markets.

### Gaps
- LiveTradeBench's capital, paper vs real status and any buy-and-hold baseline were not visible in the portion I read (~100K of 135K characters).
- AI-Trader's starting capital and real vs paper status are not stated in the paper. Current dashboard figures were not retrieved.
- No FinRL contest live-phase results were found.
- I did not review InvestorBench ([arXiv 2412.18174](https://arxiv.org/pdf/2412.18174)) in detail. It is a benchmark of LLM financial decision tasks and did not appear to be a forward/live test, so it is not counted here.
- The Rallies.ai live leaderboard (rallies.ai/arena) did not render without JavaScript, so current standings and per-model numbers for the other ~7 models were not verified.

---

## 3. Publicized real-money or forward-paper LLM stock-picking experiments

### Takeaway
The viral experiments look very different at the finish line than in their early headlines. The "ChatGPT micro-cap experiment" was reported in Aug 2025 at +23.8% after 4 weeks. It ended Dec 2025 at $82.88 from $100 (−17.1%) vs the S&P 500's +11.7% over the same window, with a −50% drawdown, and the loss got little press. Finder's ChatGPT "fund" (+57.8% in ~3 years) is hypothetical and benchmarked against a weak, partly non-equity peer set. 2026 "Claude/DeepSeek portfolio" claims on copy-trading apps are unaudited marketing with human involvement.

### Cited Findings

| Experiment | Who | Model | Assets | Period | Capital | Real/paper | Result | Benchmark (same period) | Max DD | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Micro-Cap Experiment | Nathan Smith (GitHub LuckyOne7777) | ChatGPT | US micro-caps < $300M | Jun 27 – Dec 26/27, 2025 | $100 | README says "real-money"; no broker statements | **$82.88 final (≈ −17.1%)** | S&P 500: $100 → $111.68 (+11.7%) | −50.33% (Nov 6, 2025) | D |
| Finder.com ChatGPT fund (UK) | Finder | ChatGPT (2023) | 38 stocks, equal weight, USD tracked → GBP | Mar 3, 2023 – Mar 27, 2026 | Hypothetical | Paper ("conceptual experiment") | **+57.8%** | Average of 10 most popular UK funds: +36.49% | n/a | D |
| "Claude Portfolio" on Autopilot | Pseudonymous @theaiportfolios | Claude Code (Opus 4.6) + human rails | ~15 US stocks | Mar 3 – Aug 4, 2026 | $50K | Real (claimed); ~$27M subscriber capital mirrors it | **+19.04%** | S&P 500 +12.24% | Not reported | E |
| Rallies.ai arena (ChatGPT) | Rallies AI | ChatGPT | US stocks | Late Nov 2025 – ~Jun 21, 2026 | $100K | Paper | **+72.4%** | S&P ≈ +11.3% | Not reported | D |

**ChatGPT Micro-Cap Experiment** (Nathan Smith)
- The README says "a large language model (ChatGPT) manages a real-money portfolio under strict, predefined rules", "starting with just $100". Benchmarks are the S&P 500 and Russell 2000 ([README](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment/blob/main/README.md)).
- **Early headlines:** after ~4 weeks the portfolio was +23.8% vs Russell 2000 +3.9% and XBI +3.5%. CADL generated roughly 50% of profits ([Daily Galaxy](https://dailygalaxy.com/2025/08/student-gave-chatgpt-100-to-invest-in-stock-market-four-weeks-later-his-portfolio-outperformed-wall-street/); [Benzinga](https://www.benzinga.com/markets/equities/25/08/46783783/redditors-100-chatgpt-day-trading-experiment-trounces-two-benchmark-indexes-with-24-returns-heres-how-it-pulled-it-off)).
- **Final week post (Dec 29, 2025)** ([Substack Week 26](https://nathanbsmith729.substack.com/p/chatgpts-micro-cap-portfolio-week-e93)):
  - Final equity **$82.88** (cash $4.21; holdings MIST, SLS, JSPR).
  - S&P 500 equivalent of $100 → **$111.68**.
  - Max drawdown **−50.33% on 2025-11-06**.
  - Annualized Sharpe −0.2429, Sortino −0.2836.
  - CAPM vs S&P: beta 1.133, annualized alpha **−34.31%**, R² 0.027 (124 observations).
- **Evaluation report** ([LLM-Trading-Lab](https://github.com/LuckyOne7777/LLM-Trading-Lab/blob/main/Experiments/chatgpt_micro-cap/evaluation/evaluation_report.md)):
  - Trading: 46 realized lot exits, 50% lot win rate, profit factor 0.82, expectancy −$0.41 per lot, average hold ≈17.8 days.
  - Accounting: "no transaction costs, commissions, or bid-ask spread modeled"; data "blended and reconstructed, not broker-grade accounting".
  - Run conditions: a single run, and temperature was not fixed.
  - Equity low: $67.10 on Nov 6, 2025.
  - The report notes the model "sometimes hallucinated rationale in Deep Research reports".
- **Conflicting coverage:** Switzer claimed Smith "pulled the plug" after 10 weeks at +32% ([Switzer](https://switzer.com.au/someone-let-ai-fully-control-their-stock-portfolio-heres-how-it-did/)). That contradicts the author's own Week 26 post.
- **Follow-ups:** the author's next experiment uses IPOs listed within 5 years, and he built a benchmarking framework (LIBB) ([Week 26](https://nathanbsmith729.substack.com/p/chatgpts-micro-cap-portfolio-week-e93); [README](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment/blob/main/README.md)).

**Finder.com ChatGPT fund (UK)** ([Finder tracker, updated Mar 30, 2026](https://www.finder.com/uk/share-trading/share-trading-research/ai-investing))
- **Setup:** created 3 Mar 2023, 38 equal-weighted stocks picked by ChatGPT on quality criteria (low debt, growth, competitive advantage) drawn from the 10 funds. Tracked in USD and converted to GBP. Described as a "conceptual experiment", not real money. The page says ChatGPT was "only trained on data up to 2021".
- **Result:** **+57.8% as of 27 Mar 2026** vs **36.49%** average for the 10 most popular UK funds (Interactive Investor, March 2023 list). ChatGPT "has led the real funds for 99% of its lifespan". No S&P 500 or MSCI World comparison is given.
- **Benchmark funds:** Fundsmith; Vanguard LifeStrategy 100/80/60; Vanguard FTSE Dev World ex-UK; Vanguard US Equity Index; Vanguard FTSE Global All Cap; HSBC FTSE All-World; Fidelity Index UK; Fidelity Index World.
- **Early result:** +4.9% in the first two months vs −0.8% for the 10 funds ([Business Standard, May 2023](https://www.business-standard.com/technology/tech-news/portfolio-created-by-chatgpt-reports-better-returns-than-top-funds-in-uk-123050500240_1.html)). A later update said it led by ~14 pp with the funds up 27.63% ([European Business Magazine](https://europeanbusinessmagazine.com/finders-chatgpt-investment-fund-is-still-outperforming-the-uks-10-most-popular-funds/)).
- **Critique:** Andrew Rice: "I don't believe they used an appropriate benchmark". Two of the funds hold only 80% and 60% equity ([Algomodels](https://algomodels.com/chatgpt-the-stock-picker/)). eToro's Dan Moczulski warned that generic models misquote figures and dates and lean on narrative ([Slashdot/Reuters](https://slashdot.org/story/25/09/25/1948246/experts-urge-caution-about-using-chatgpt-to-pick-stocks)).

**Other public experiments, 2025–2026**
- **"Claude Portfolio" on Autopilot** ([explainx.ai, Aug 2026](https://explainx.ai/blog/claude-portfolio-autopilot-ai-trading-experiment-august-2026)):
  - $50K real-money account from Mar 3, 2026. A Claude Code agent (Opus 4.6) researches about 15 positions, reviewed twice a week.
  - **+19.04% vs S&P +12.24%** as of the operator's Aug 4, 2026 post.
  - The operator sets risk rails and makes final trade decisions, so this is not autonomous. About $27M in subscriber capital mirrors the trades. Sharpe, max drawdown and volatility are not reported, and no audit exists.
  - The organizer reportedly runs seven AI-branded portfolios (~$200M combined). A DeepSeek-based portfolio there was reportedly ~+56% over a prior 12-month window vs ~+16% for the S&P 500.
  - explainx attributes the organizer to "AI Finance Labs", run by finance professor Alejandro Lopez-Lira. I could not verify this independently.
  - Anthropic did not build or endorse it. SEC registration of the platform (Autopilot Advisers LLC) "does not validate the portfolio's return claims".
- **Yahoo Finance UK:** ChatGPT's five UK picks for 2025 averaged about −4.4% at mid-year. Tesco and Shell were up; three were down ([Yahoo Finance UK](https://uk.finance.yahoo.com/news/chatgpt-picked-5-uk-stocks-060143347.html)).
- **Small anecdote:** a writer gave Claude $100 and a crypto wallet. After ~1.5 weeks the account was at $96.49 (PnL −$2.77 on $7,591 volume) ([Substack](https://vincentmayeski.substack.com/p/i-gave-claude-100-and-a-crypto-wallet)). Tier D.
- **Viral claims:** a "Claude-powered Polymarket bot turned $1,000 into $14,216 in 48 hours". The same source notes on-chain data showing 92.4% of Polymarket wallets lose money ([Medium](https://medium.com/@weare1010/claude-ai-trading-bots-are-making-hundreds-of-thousands-on-polymarket-2840efb9f2cd)). Tier E, unverified.

### Inferences
- **The micro-cap experiment is a textbook case of early-snapshot bias.** The widely syndicated +23.8% (4 weeks) became −17.1% (6 months). That is ≈28.8 pp behind the S&P 500 (my calculation: −17.1% vs +11.7%), with annualized alpha of −34%. The ending was covered far less than the start.
- **Finder's "outperformance" is plausibly explained by US equity exposure.** It compares a 100%-equity, US-listed quality basket against a peer set that includes 60%/80% equity multi-asset funds and a UK index fund. No like-for-like equity benchmark is given, so it does not show stock-picking skill.
- **All positive 2026 "AI portfolio" claims fail at least one test:** paper money (Rallies), human-in-the-loop with unaudited returns (Autopilot "Claude Portfolio"), or a short window in a rising market (5–7 months). They are also subject to selection: platforms that run 7–8 AI portfolios advertise the best one.

### Gaps
- No broker statements for the micro-cap experiment were found. Russell 2000/IWO/XBI returns for the full Jun 27 – Dec 26, 2025 window were not reported in the final post.
- I found no S&P 500 or MSCI World (GBP) return for Finder's Mar 2023 – Mar 2026 window, which would be the like-for-like comparison.
- Claude Portfolio: the trade log, drawdown and the human vs Claude split of decisions are unaudited. The organizer identity comes only from explainx.ai.
- I did not find any verified, ongoing public real-money dashboard for Claude/Gemini/Grok portfolios beyond Alpha Arena.

---

## 4. AI-driven ETFs and funds with public live NAV track records

### Takeaway
The longest live AI fund records are mostly negative relative to the S&P 500:
- **AIEQ** (launched Oct 2017) roughly doubled (+100.2%) while the S&P 500 roughly tripled (+199.7%) by Aug 2026.
- A peer-reviewed census of 54 AI ETFs and mutual funds found that **all 11 fully AI funds lagged the S&P 500** (−1.8%/yr vs +7.6%/yr), and **31 of 54 had closed**.
- **Qraft** liquidated QRFT (Jul 2026) and NVQ, and rebranded AMOM under Defiance as an "LLM" fund.
- **BUZZ** returned ~5.3%/yr vs ~14.2% for the S&P 500.
- The **Eurekahedge AI Hedge Fund Index** returned 9.8% vs 13.7% annualized over 2009–2024.

Exceptions with strong recent numbers (AMOM in 2024, Numerai in 2024, High-Flyer in 2025) are survivors or private funds reporting their own results.

### Cited Findings

| Fund / index | Launch | Status (Nov 2026) | Live record vs benchmark | Fees | Tier |
|---|---|---|---|---|---|
| AIEQ (Amplify AI Powered Equity ETF) | Oct 17, 2017 | Active; AUM $104.7M | +100.2% since inception vs S&P ≈ +199.7% (to ~Aug 2026); 63% vs 108% through Dec 31, 2023 | 0.75% | B |
| QRFT (QRAFT AI-Enhanced US Large Cap) | Not retrieved | **Liquidated ~Jul 24, 2026** | Not retrieved | n/a | B |
| AMOM → AIED (Defiance LLM Catalyst Momentum ETF) | May 20, 2019 | Active under Defiance since Jul 1, 2026; ticker AIED (Oct 19, 2026); AUM $21–27M | 2024: +35.79% vs S&P +24.89%; 3-yr ≈ 83.4%, 5-yr ≈ 54.5% (Mar 19, 2026) | 0.75% | B |
| NVQ (QRAFT AI-Enhanced US Next Value) | n/a | **Liquidated**; $33.5954/share cash | Not retrieved | n/a | B |
| BUZZ (VanEck Social Sentiment ETF) | Mar 2, 2021 | Active | ≈ 5.3%/yr since inception vs S&P ≈ 14.2%/yr | n/a | B |
| LIVR (Intelligent Livermore ETF) | Sep 2024 | Active | Since-inception price return +14.9% to Dec 31, 2025; 2025 +24.85% | 0.69% | B |
| AIVL (WisdomTree US AI Enhanced Value) | n/a | Active | YTD 8.20% vs S&P 12.68%; 1-yr 11.50% vs 18.34% (Aug 2026) | 0.38% | B |
| Finq AIUP / AINT | Recent | Active | YTD 11.59% / 19.68% vs S&P 12.68% (Aug 2026) | 0.75% | B |
| Eurekahedge AI Hedge Fund Index | Index from Dec 2009 | Legacy indices sunsetting 2025 | 9.8% vs 13.7% annualized (Dec 2009 – Jul 2024) | n/a | D |
| Numerai One (hedge fund) | n/a | Active; ~$450M AUM (Aug 2025) | 2024 +25.45% net (Sharpe 2.75); 2025 ≈ +6% net to Aug vs 7% quant-EMN index | 1% / 20% | D |
| High-Flyer (DeepSeek parent quant) | n/a | Active; >70bn yuan | 2025 average +56.6% vs China quant average 30.5% | n/a | D |
| Bridgewater AIA Macro | Jul 2024 (~$2B) | Active; >$5B raised | 2025 ≈ +11%; H1 2026 +8.1% (same as Pure Alpha); 11.3% annualized since inception | n/a | D |

**AIEQ**
- 24/7 Wall St (republished by Yahoo, Aug 26, 2026) reports that AIEQ "has gained 100.2%" since its Oct 17, 2017 launch, vs "roughly 199.7%" for the S&P 500. AIEQ "didn't implode, but it also didn't demonstrate that artificial intelligence could consistently outsmart a simple index fund." Same article: YTD 11.90% vs S&P 12.68%; 1-yr 16.12% vs 18.34%; expense ratio 0.75% vs 0.03% for some S&P ETFs ([Yahoo/24/7 Wall St](https://finance.yahoo.com/markets/stocks/articles/ai-help-beat-stock-market-152310707.html)).
- Average annual return of **8.48%** since inception, 1-yr total return 5.08%, AUM $104.70M, expense ratio 0.75% (as of Nov 23, 2026) ([StockAnalysis](https://stockanalysis.com/etf/aieq/)).
- **63% cumulative total return through Dec 31, 2023 vs 108% for the S&P 500** ([Scientific American, Wyatt & Smith, Aug 23, 2024](https://www.scientificamerican.com/article/ai-makes-unreliable-investment-decisions/)).
- Since Jan 2024: annualized alpha −5.08%, beta 1.13 vs S&P ([PortfoliosLab](https://portfolioslab.com/symbol/AIEQ)). Seeking Alpha calls it an "unconvincing AI-driven strategy still lagging the market" ([Seeking Alpha](https://seekingalpha.com/article/4949900-aieq-unconvincing-ai-driven-strategy-still-lagging-the-market)).

**Wyatt & Smith census** (Journal of Investing 2025, "The Disappointing Performance of AI-Powered Funds") ([Journal of Investing](https://www.pm-research.com/content/iijinvest/34/3/74); [Scientific American](https://www.scientificamerican.com/article/ai-makes-unreliable-investment-decisions/))
- The sample is 54 AI-driven ETFs and mutual funds launched since Oct 18, 2017.
- **11 fully AI funds:** "every single one did worse than the S&P 500". They averaged **−1.8%/yr vs +7.6%** for the S&P. 6 of 11 lost money, and 6 of 11 shut down.
- **43 partly AI funds:** 10 beat the S&P. They averaged **7.11% vs 12.43%**, and 25 of 43 shut down.
- MIND (shut 2022) returned −12% vs S&P +65%.

**Qraft**
- **QRFT:** liquidation announced Jun 30, 2026. Last trading ~Jul 21 and liquidation ~Jul 24, 2026 ([PR Newswire](https://www.prnewswire.com/news-releases/exchange-traded-concepts-to-close-and-liquidate-qraft-ai-enhanced-us-large-cap-etf-nyseqrft-302813996.html)). The first liquidating distribution was $69.8106/share, paid Jul 27, 2026 ([OCC memo](https://infomemo.theocc.com/infomemos?number=59457)).
- **NVQ:** listed as liquidated, with $33.5954/share paid in cash ([Bloomberg quote page](https://www.bloomberg.com/quote/NVQ:US); [Robinhood tracker](https://robinhood.com/gb/en/support/articles/corporate-actions-tracker/)). The tracker's entries are dated Feb 2024, so the timing is uncertain.
- **AMOM → AIED** ([BriefGlance, Oct 19, 2026](https://briefglance.com/articles/can-llms-fix-momentum-investing-defiance-bets-on-real-time-ai)):
  - Defiance took over as sponsor on Jul 1, 2026 and renamed the fund **Defiance LLM Catalyst Momentum ETF (AIED)**.
  - It adds LLM real-time news scoring to the prior deep-learning momentum model. Qraft remains the AI licensor.
  - AUM $21–27M; expense ratio 0.75%.
  - Returns: 2024 **+35.79% vs S&P +24.89%**; 2026 YTD +21.68%.
  - 3-yr ≈ 83.4% and 5-yr ≈ 54.5% total return as of Mar 19, 2026 ([Seeking Alpha](https://seekingalpha.com/symbol/AMOM/momentum/performance)). The ticker change to AIED was dated Oct 19, 2026 ([Robinhood](https://robinhood.com/gb/en/support/articles/corporate-actions-tracker/)).
  - AMOM YTD was 19.84% vs S&P 12.68% (Aug 2026) ([Yahoo/24/7](https://finance.yahoo.com/markets/stocks/articles/ai-help-beat-stock-market-152310707.html)).

**BUZZ**
- VanEck's table shows average annual returns since the Mar 2, 2021 inception of ≈5.3% (NAV) vs ≈14.2% for the S&P 500. This is a snapshot about 52 days old, taken via search snippet; the page itself did not load ([VanEck](https://www.vaneck.com/us/en/investments/social-sentiment-etf-buzz/)).
- Calendar years: 2022 −47.67% vs −19.44%; 2023 +54.64% vs +24.23% ([Yahoo Finance](https://finance.yahoo.com/quote/BUZZ/performance/); [PortfoliosLab](https://portfolioslab.com/symbol/BUZZ)).

**LIVR**
- Launched Sep 2024 ([Benzinga](https://www.benzinga.com/markets/equities/24/09/41018183/did-aping-warren-buffett-and-hedge-fund-managers-bring-success-to-this-ai-powered-etf-that-launc)).
- Calendar returns: 2024 −3.22% (partial year), 2025 +24.85%, 2026 YTD +2.17%. Max drawdown −23.66% ([Alphacubator](https://www.alphacubator.com/analysis/LIVR)).
- Since-inception price return 14.9% as of Dec 31, 2025; beta 1.03; R² 64% ([ETFRC](https://www.etfrc.com/LIVR)).

**Eurekahedge AI Hedge Fund Index**
- 9.8% annualized vs S&P 500 13.7% from Dec 2009 to Jul 2024, per EurekaHedge/Hulbert Ratings. The index did relatively better in the first half of the sample ([IG, Nov 26, 2024](https://www.ig.com/za/prime/insights/articles/has-artificial-intelligences-impact-on-hedge-funds-been-overhype-241121)).
- Legacy Eurekahedge indices are "sunsetting in 2025" ([With Intelligence](https://www.withintelligence.com/eurekahedge-data-on-with-intelligence/)).

**Numerai**
- Numerai One returned **+25.45% net in 2024** (Sharpe 2.75, a single down month), net of 1%/20% fees. AUM went from $60M to $450M over three years, and JPMorgan committed $500M of capacity. Signals include "tree ensembles, transformers, and LLM-reasoning-based signals". No audit statement is given ([Numerai blog, Aug 26, 2025](https://blog.numer.ai/jpmorgan-secures-500m-capacity/)).
- 2025: ~+6% net through Aug vs 7% for Aurum's quant equity market-neutral index ([Hedgeweek](https://www.hedgeweek.com/quant-hedge-fund-numerai-secures-500m-jpmorgan-allocation/)). About +8% through Oct, per the founder via a secondary source ([Bitget](https://www.bitget.com/news/detail/12560605074172)).

**High-Flyer**
- Average **+56.6%** across funds in 2025, per PaiPaiWang data, vs 30.5% for China quant funds overall ([Bloomberg, Jan 12, 2026](https://www.bloomberg.com/news/articles/2026-01-12/deepseek-founder-liang-s-funds-surge-57-as-china-quants-boom)). It ranked 2nd among China's top-10 large hedge-fund firms behind Lingjun (+73.5%) ([SCMP](https://www.scmp.com/tech/tech-trends/article/3339633/deepseek-founders-high-flyer-ranks-among-chinas-top-hedge-fund-firms-2025)).

**Bridgewater AIA**
- The fund launched Jul 2024 with machine learning as "the primary basis" of decisions ([Fortune, Jul 2024](https://fortune.com/2024/07/01/bridgewater-2-billion-fund-machine-learning-decision-making-openai-anthropic-perplexity/)).
- The CEO said its performance was "comparable" to human-run funds ([Bloomberg, Mar 4, 2025](https://www.bloomberg.com/news/articles/2025-03-04/bridgewater-ceo-says-firm-s-ai-fund-comparable-to-human-ones)).
- 2025 ≈ +11%, with >$5B raised ([Fortune, Jan 2, 2026](https://fortune.com/2026/01/02/top-hedge-fund-performers-2025-bridgewater-de-shaw-citadel-millennium/)).
- H1 2026 +8.1%, the same as Pure Alpha; 11.3% annualized since inception ([CryptoBriefing](https://cryptobriefing.com/bridgewater-macro-fund-gains-h1-2026/); [The Star](https://www.thestar.com.my/tech/tech-news/2026/07/02/bridgewater039s-flagship-macro-fund-gains-81-in-first-half-amid-market-volatility-sources-say)).

**Other evidence (low confidence)**
- Mark Hulbert (MarketWatch, ~2025) reported a study in which AI stock-trading tools lagged a basic S&P 500 fund. Syndicated summaries cite six AI tools averaging −8.4% vs S&P total return +2% ([Futu syndication](https://news.futunn.com/en/post/61551592/ai-can-do-a-lot-of-things-like-tearing-down); [Blockgeni](https://blockgeni.com/the-sp-500-is-doing-significantly-better-than-ai-tools/)). The original was not retrieved.

### Inferences
- **AIEQ annualized (my calculation from the 24/7 figures, ~8.86 years):** ≈ **8.1%/yr vs ≈ 13.2%/yr** for the S&P 500, about a 5 pp/yr gap. This is consistent with StockAnalysis's 8.48% average annual figure and with PortfoliosLab's −5% alpha. With beta ≈1.1, AIEQ behaves like a higher-beta, fee-laden closet index fund.
- **Survivorship bias is severe.** 31 of 54 AI funds in the Wyatt & Smith sample had closed by their study date, and QRFT and NVQ closed later. Any list of "AI funds that beat the market" drawn from today's live tickers therefore overstates the category.
- **Eurekahedge gap, compounded (my calculation):** 9.8% vs 13.7% over ~14.6 years is roughly 3.9× vs 6.5× growth. Hedge-fund indices also carry self-reporting and backfill bias, so the true gap is likely worse.
- **The bright spots do not establish a durable edge:**
  - AMOM is a momentum fund that did well in the 2024 momentum regime. Its 5-year total return was ≈54.5% as of Mar 2026; I did not retrieve a same-window S&P 500 figure to compare. It is now being rebranded around LLMs.
  - Numerai had a strong 2024 after a reportedly negative 2023 (unverified, ~−17%) and an ordinary 2025.
  - High-Flyer and Bridgewater AIA are ML/quant (not LLM-autonomous) funds whose numbers are self-reported or leaked. AIA merely matched its human-run sibling.
- **Rebranding is a recurring pattern.** The AMOM → "LLM Catalyst" rebrand suggests issuers are relabeling existing quant products as LLM-driven. These products need a fresh forward record under the new methodology, starting Jul–Oct 2026.

### Gaps
- I could not confirm the exact end date of the 24/7 Wall St AIEQ cumulative figures (published Aug 26, 2026). I also could not re-verify the EquBot/IBM Watson origin of AIEQ's model in this pass.
- No since-inception returns were retrieved for QRFT, NVQ or AMOM/AIED. No information was found on "HDMO". The NVQ liquidation date is uncertain (Feb 2024 per Robinhood's tracker).
- The VanEck BUZZ page failed to load (redirect loop), so its numbers come from the search snippet. LIVR, AIVL and Finq lack same-period S&P 500 since-inception comparisons.
- No calendar 2024 or 2025 figures were found for the Eurekahedge AI index (being sunset).
- The full-year 2025 Numerai return was not found, and the 2023 figure (≈ −17%) comes from secondary sources only.
- The Bridgewater 11.9% figure for 2025 (vs ~11%) appeared only in search snippets attributed to Hedgeweek, without a retrievable URL.

---

## 5. Out-of-sample academic evidence on LLM signals, and the look-ahead-bias problem

### Takeaway
The landmark Lopez-Lira & Tang result (now in the *Journal of Financial Economics*, 2026) holds up on post-cutoff data, but its economics are fragile:
- The GPT-4 news long-short strategy's annualized Sharpe fell from **6.54 (2021Q4) to 3.68 (2022), 2.33 (2023) and 1.22 (Jan–May 2024)**.
- Its ~700% cumulative gross return becomes **unprofitable at 20 bps round-trip costs**, so only market-maker-level costs could exploit it.
- Look-ahead/memorization research shows LLMs leak post-period knowledge into "historical" tests, and prompting or name-masking does not fix it. This makes forward tests the only clean evaluation.

### Cited Findings

**Lopez-Lira & Tang, "Can ChatGPT Forecast Stock Price Movements?"** ([arXiv 2304.07619](https://arxiv.org/abs/2304.07619), v6 Oct 28, 2025; [PDF](https://arxiv.org/pdf/2304.07619); published *JFE* vol. 184, 2026 per [RePEc](https://ideas.repec.org/a/eee/jfinec/v184y2026ics0304405x26001066.html))
- **Sample:** news headlines for 4,123 U.S. stocks, Oct 2021 – May 2024. Chosen "to avoid look-ahead bias", because "the training data of the ChatGPT models stops in September 2021".
- **Signal:** a long-short daily-rebalanced strategy on GPT-4 assessments of overnight news earned **34 bps/day before costs**. The drift-strategy annualized Sharpe was **2.97**, vs 1.66 for GPT-3.5 and 1.26 for DistilBART-MNLI.
- **Cost sensitivity:**
  - Cumulative return "around 700% from 2021m10 to 2024m5" with no transaction costs.
  - ">300%" at 5 bps round-trip and ">100%" at 10 bps.
  - "A transaction cost of 20 bps round-trip makes the strategy unprofitable."
  - Turnover is ≈190% per day.
  - Exploitation is "only feasible for market participants whose transaction costs are sufficiently low, such as market makers".
- **Decay:** "the annualized Sharpe ratio declines from 6.54 in 2021Q4 to 3.68 in 2022, 2.33 in 2023, and 1.22 over January–May 2024". The authors read this as LLM adoption improving efficiency. For intraday news, the implementable close-to-close strategy "becomes insignificant in January–May 2024".
- **Hit rates:** about 90% portfolio-day hit rates, but on the *non-tradable* initial reaction ([abstract](https://arxiv.org/abs/2304.07619)).
- **Memorization warning:** the paper cites Sarkar & Vafa (2024) and Lopez-Lira, Tang & Zhu (2025) as "strong evidence that one must use a sample period after an LLM's knowledge cutoff date to avoid lookahead bias and memorization problems" ([PDF](https://arxiv.org/pdf/2304.07619)).

**Forward-in-time (live) academic test: Pelster & Val (2024), *Finance Research Letters* 59, 104786** ([RePEc](https://ideas.repec.org/a/eee/finlet/v59y2024ics1544612323011583.html); [Marginal Revolution](https://marginalrevolution.com/marginalrevolution/2023/11/can-chatgpt-assist-in-picking-stocks.html))
- A live experiment during the Q2 2023 earnings season. GPT-4 rated stock attractiveness over the next month on a −5 to +5 scale and forecast earnings.
- The ratings were positively related to subsequent earnings surprises and returns, but accuracy varied over time.
- The authors frame LLMs as "assistants" in stock selection, not the final judgment. A later study cites this paper and states that ChatGPT's recommendations "lack consistency and are sensitive to prompt design".

**Look-ahead bias and memorization evidence**
- **Sarkar & Vafa (2024)** ([SSRN 4754678](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4754678), summarized in [FINM 33200 notes](https://finm-33200.github.io/discussions/llms_and_lookahead_bias.html)):
  - When asked about risks from Sept–Nov 2019 earnings calls, **6.8% of LLM outputs mention "COVID-19"**.
  - Supply-chain-disruption mentions are ~35% more common for 2020 vs 2019 given structurally identical inputs.
  - Prompting ("only consider information up to 2019") and firm-name masking are insufficient: models identify masked firms **~70%** of the time.
- **Glasserman & Lin (2023)** ([SSRN/ResearchGate](https://www.researchgate.net/publication/374930572_Assessing_Look-Ahead_Bias_in_Stock_Return_Predictions_Generated_By_GPT_Sentiment_Analysis)): an early systematic study of look-ahead bias in GPT sentiment-based return prediction. A secondary summary reports that anonymized headlines outperformed originals in-sample, attributed to a "distraction effect", especially for larger firms.
- **Lopez-Lira, Tang & Zhu (2025), "The Memorization Problem: Can We Trust LLMs' Economic Forecasts?"** ([ResearchGate](https://www.researchgate.net/publication/390924734_The_Memorization_Problem_Can_We_Trust_LLMs'_Economic_Forecasts)): cited as evidence that LLMs memorize pre-cutoff economic and financial data. I did not retrieve its specific numbers.
- **Engelberg, Manela, Mullins & Vulicevic (2025), "Entity Neutering"** ([SSRN 5182756](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5182756), via [FINM notes](https://finm-33200.github.io/discussions/llms_and_lookahead_bias.html)):
  - ChatGPT identifies the firm in **0.11%** of neutered texts vs **69.1%** with simple name-masking.
  - Look-ahead bias accounts for at most 12% (binary sentiment) to 36% (strong/weak) of the predictive power on Dow Jones news.
- **He, Lv, Manela & Wu (2025), "Chronologically Consistent LLMs"** ([arXiv 2502.21206](https://arxiv.org/abs/2502.21206)): time-sliced ChronoBERT and ChronoGPT trained 1999–2024 give long-short Sharpes of 4.80 and 4.92 vs 4.90 for Llama 3.1 (Dow Jones Newswire, 2007–2023). Look-ahead bias was "modest" for that news-sentiment application.
- **Further work:**
  - A statistical test for lookahead bias in LLM forecasts: Gao, Jiang & Yan ([arXiv 2512.23847](https://arxiv.org/pdf/2512.23847)).
  - An Economics Letters paper finding minimal memorization effects for high-frequency individual-stock data with GPT-4.1 ([orbilu PDF](https://orbilu.uni.lu/bitstream/10993/68692/1/1-s2.0-S0165176525004392-main.pdf)).
  - HindsightBench ([arXiv 2607.18867](https://arxiv.org/pdf/2607.18867)) and MemGuard-Alpha ([arXiv 2603.26797](https://arxiv.org/pdf/2603.26797)).
- **Benchmark authors on leakage:** LiveTradeBench argues live streaming "eliminat[es] dependence on offline backtesting and prevent[s] information leakage" ([arXiv](https://arxiv.org/html/2511.03628)). FINSABER attributes earlier LLM edges to survivorship and data-snooping biases ([arXiv](https://arxiv.org/abs/2505.07078)).

**Verification tier: C** for all items in this section. Even the post-cutoff studies are historical replays, not live trading, except Pelster & Val's live rating exercise, which reports no trading P&L in the sources I saw.

### Inferences
- **The strongest LLM signal in the literature is an alpha-decay story.** It is real on post-cutoff data, but it is a high-turnover, small-cap-tilted, cost-fragile anomaly. Its Sharpe fell by about 80% in 2.5 years, and it needs costs below 20 bps round-trip. A retail-scale LLM bot that trades news is unlikely to capture it.
- **Look-ahead contamination varies by task.**
  - It is large for tasks where the model can recognize the firm, the date and the outcome: earnings-call risk narratives, famous events, price levels.
  - It is smaller for high-frequency, anonymized news sentiment (Chrono-LLMs, entity neutering).
  - It is likely severe for agentic "trader" backtests that let an LLM reason about named stocks over periods it was trained on.
  - Any LLM trading backtest that covers dates before the model's training cutoff should be treated as invalid unless chronologically consistent models or neutered inputs are used.
- **Synthesis across sections:**
  - Tier A (on-chain) evidence, from Alpha Arena, is negative.
  - Tier B (public NAV) evidence, from AI ETFs, is mostly negative vs the S&P 500, with high closure rates.
  - Tier C live benchmarks show returns mostly explained by beta, with no robust alpha.
  - The positive headline claims (Rallies, Autopilot portfolios, Finder) are tier D/E: paper money or unaudited, short-window and winner-selected.
- **What a GitHub "LLM trader skill" repo would need before being credible** (my inference from the above):
  - Timestamped forward results, ideally broker-linked or on-chain (tier A), over at least several months and multiple market regimes.
  - Comparison to buy-and-hold of the same universe, net of fees, funding and slippage.
  - Multiple runs or seeds to show the outcome is not one lucky path.
  - A disclosed model version and prompt, frozen before the test.
  - Repos with thousands of stars but only backtests (ai-hedge-fund, TradingAgents-style frameworks) provide no such evidence.

### Gaps
- I could not retrieve the original April 2023 Lopez-Lira & Tang figures, which are widely misquoted in press as "500%" returns. The ~700% gross figure above is from the v6 sample (Oct 2021 – May 2024).
- Exact numbers from Glasserman & Lin and from the "Memorization Problem" paper were not retrieved, and Pelster & Val's effect sizes were not retrieved either. All three are summarized from abstracts or secondary sources.
- I found no study that live-trades an LLM strategy with real money over more than a year with independent verification. That absence is itself a key finding: as of Nov 2026, the longest verified forward records of "AI" investing are the AI ETFs (since 2017), and they lag the S&P 500.
