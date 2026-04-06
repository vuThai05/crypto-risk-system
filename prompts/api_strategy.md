We are designing the API call strategy for a crypto market risk analytics system.

IMPORTANT:
This is NOT a coding task yet.
You must think like a system designer and challenge assumptions.

---

CONTEXT:

* API provider: CoinGecko
* Limit: 500 calls/day
* Rate limit: 25 calls/minute

SYSTEM GOAL:

* Analyze market risk (NOT price prediction)
* Focus on Top 100 cryptocurrencies
* Transform raw data into risk signals
* Prioritize market-level understanding over individual coin analysis

---

CURRENT STRATEGY (PROPOSED):

1. MARKET DATA (CORE)

   * Endpoint: /coins/markets
   * Fetch top 100 coins
   * Frequency: every 5 minutes (~288 calls/day)

2. COIN TIME SERIES (SELECTIVE)

   * Endpoint: /coins/{id}/market_chart
   * Only top 20 coins
   * Frequency: 2 times/day (~40 calls/day)

3. METADATA

   * Endpoint: /coins/{id}
   * Fetch once at system initialization (~100 calls total)
   * No repeated daily calls

TOTAL USAGE:
~330 calls/day (safe under 500)

---

ASSUMPTIONS:

* Market endpoint provides enough signal for most risk metrics
* Coin-level time series is only needed for refinement
* Top 20 coins represent majority of market movement
* Metadata is mostly static and not needed frequently

---

YOUR TASK:

1. CRITICALLY EVALUATE this strategy:

   * What is inefficient?
   * What is missing?
   * What assumptions might be wrong?

2. SUGGEST IMPROVEMENTS:

   * Better allocation of API calls
   * Smarter scheduling (time-based or event-based)
   * Whether frequency should change (e.g. adaptive intervals)

3. PROPOSE ALTERNATIVE STRATEGIES:

   * If we reduce calls further, what do we lose?
   * If we increase coin coverage, what improves?

4. THINK IN TERMS OF SIGNAL vs COST:

   * Which API calls generate the most useful information?
   * Which ones are wasteful?

5. DO NOT WRITE CODE

---

OUTPUT FORMAT:

* Evaluation of current design
* Identified weaknesses
* Improved strategy (clear and actionable)
* Optional advanced ideas (if applicable)

---

IMPORTANT:

* Be critical, not agreeable
* Avoid generic answers
* Focus on real system trade-offs