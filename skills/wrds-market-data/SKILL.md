---
name: wrds-market-data
description: Use WRDS Cboe VIX, restricted Cboe options end-of-day samples, and OTC Markets end-of-day prices. Verify table-specific identifiers, dates, prices, volatility units, and coverage before extraction.
---

# Cboe and OTC market data on WRDS

Load [wrds-catalog](../wrds-catalog/SKILL.md) for exact columns and [wrds-psql](../wrds-psql/SKILL.md) for execution. [Coverage](references/catalog-coverage.md) lists every selected table.

| Request | Product |
|---|---|
| Cboe VIX time series | `cboe_all.cboe` |
| OTC end-of-day prices | `otc_endofday.endofday` |
| Cboe option end-of-day prototype | `cboe_sample`: `eqmaster`, `eqprice`, `eqhvol`, `optcontract`, `optprice`, `ivlisted`, `wrds_eq_opt_merged` |

The Cboe option tables here are a restricted sample. They are a different product from OptionMetrics, the Cboe C1 trade-by-trade archive, and TAQ. Use [wrds-optionmetrics](../wrds-optionmetrics/SKILL.md) for IvyDB; use [wrds-taq](../wrds-taq/SKILL.md) for raw TAQ.

Start with one security and one week. Read the exact table comments before deciding whether a field is a close, settlement, bid, ask, theoretical value, percent volatility or decimal volatility. Establish the underlying and option contract identifiers separately, including expiration, strike scale, option type and contract adjustment fields supplied by the product. Do not join options using only an underlying ticker.

For OTC work, preserve original symbols and security identifiers; symbol changes and inactive instruments can affect a history. Confirm date coverage and the treatment of missing/stale quotes before computing returns. For VIX, report an index level as an index level unless the user explicitly asks for a derived change or investment strategy; it is not itself a tradable total-return series.

Primary sources: [WRDS Cboe product descriptions](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/cboe-chicago-board-options-exchange/), [WRDS OTC Markets products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/otc-markets-group/). Their current dictionary links and retrieval dates are in the catalog. Do not infer access to a full product from its sample.
