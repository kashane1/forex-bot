# Sources and Evidence Notes

Date checked: 2026-05-21

## Official broker/platform docs

- OANDA v20 REST API introduction: https://developer.oanda.com/rest-live-v20/introduction/
- OANDA pricing and candles endpoints: https://developer.oanda.com/rest-live-v20/pricing-ep/
- OANDA order endpoints: https://developer.oanda.com/rest-live-v20/order-ep/
- OANDA transaction endpoints: https://developer.oanda.com/rest-live-v20/transaction-ep/
- OANDA account and instrument endpoints: https://developer.oanda.com/rest-live-v20/account-ep/
- OANDA instrument definitions: https://developer.oanda.com/rest-live-v20/instrument-df/
- OANDA Python samples: https://github.com/oanda/v20-python-samples
- QuantConnect Lean CLI docs: https://www.quantconnect.com/docs/v2/lean-cli
- QuantConnect Lean OANDA brokerage docs: https://www.quantconnect.com/docs/v2/lean-cli/live-trading/brokerages/cfd-and-forex-brokerages
- QuantConnect Lean OANDA brokerage plugin: https://github.com/QuantConnect/Lean.Brokerages.OANDA
- FOREX.com API trading page: https://www.forex.com/en/trading-tools/api-trading/
- MetaTrader5 Python package on PyPI: https://pypi.org/project/MetaTrader5/

## Risk and regulation

- CFTC forex fraud advisory: https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/fraudadv_forex.html
- CFTC forex customer advisory: https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html
- eCFR 17 CFR 4.41, simulated or hypothetical performance limitations: https://www.ecfr.gov/current/title-17/chapter-I/part-4/subpart-D/section-4.41
- OANDA US margin rates and leverage ratios: https://www.oanda.com/us-en/legal/margin-rates/

## Strategy/research background

- Moskowitz, Ooi, Pedersen, Time Series Momentum: https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum
- Hurst, Ooi, Pedersen, A Century of Evidence on Trend-Following Investing: https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/
- Brunnermeier, Nagel, Pedersen, Carry Trades and Currency Crashes: https://www.nber.org/papers/w14473
- Bailey, Borwein, Lopez de Prado, Zhu, The Probability of Backtest Overfitting: https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- Bailey and Lopez de Prado, The Deflated Sharpe Ratio: https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

## How to interpret this evidence

The sources justify engineering feasibility and broad strategy-family research, not an expected profit. OANDA/Lean docs show that the platform path is plausible. Trend-following research supports a candidate hypothesis. CFTC/eCFR materials warn that forex and hypothetical backtests have substantial limitations. The repo must treat backtests as fragile evidence and practice trading as an execution-quality test, not as proof of future profitability.
