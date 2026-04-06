Implement the risk scoring engine for the crypto system.

REQUIREMENTS:

1. Follow clean service pattern:

   * pure functions
   * no DB access inside logic

2. Input features:

   * volatility
   * drawdown
   * returns

3. Normalize features before scoring

4. Risk formula:
   risk_score = weighted sum (config-driven)

5. Output:

   * score (0–100)
   * level (0–25: Low, 26–50: Medium, 51–75: High, 76–100: Extreme)

6.  

   Scenario Thinking:

   * low volatility → low risk
   * high drawdown → high risk
   * sudden spike → extreme risk

     

7. Edge cases:

   * missing data
   * extreme volatility

8. Testing:

   * unit tests for each function
   * edge cases
   * deterministic results

OUTPUT:

* risk_engine.py
* test_risk_engine.py
* explanation of scoring logic  