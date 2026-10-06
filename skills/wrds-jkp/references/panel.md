# JKP panel selection and timing

The [provider's WRDS guide](https://jkpfactors.com/jkp-wrds-guide) documents its stock-level sample and identifiers. Its four screens select common shares, principal exchanges, the primary security, and the preferred observation where CRSP and Compustat overlap. Country selection and factor-definition files are separate inputs. Retain their versions with an extraction.

The [provider data page](https://jkpfactors.com/data) distinguishes the WRDS stock panel from distributed characteristic-managed factor returns. The downloadable factor-return set uses 153 characteristics; factor returns have their own weighting, sign, currency, and excess-return definitions. A stock characteristic is not itself that factor's payoff.

## Current product and exact fields

Catalog evidence was collected 2026-10-05. Use [wrds-catalog](../../wrds-catalog/SKILL.md) for all fields, comments, aliases, and access/lifecycle evidence.

| `contrib_global_factor` table | Observed columns | Use |
|---|---:|---|
| `global_factor` | 444 | General monthly stock-characteristic panel |
| `ctff_chars` | 410 | Common Task Framework characteristics, including `id`, `eom`, `eom_ret`, `ret_exc_lead1m`, `ctff_test` |
| `ctff_daily_ret` | 3 | `id`, `date`, `ret_exc` daily-return companion |
| `ctff_features` | 1 | `features` list; inspect its representation before using it |

The corresponding `contrib.*` aliases point to the current product family. Treat the Common Task Framework tables as their own research dataset: inspect its current [rules](https://jkpfactors.com/ctf/rules) and [dataset documentation](https://jkpfactors.com/ctf/dataset-access) before changing a designated split or merging targets. Do not assume `ctff_chars` and `global_factor` are interchangeable simply because they share fields.

Key fields on `global_factor`:

| Purpose | Fields and distinctions |
|---|---|
| Stock and issuer identity | `id`, `permno`, `gvkey`; the first two are numeric in this snapshot, `gvkey` is text |
| Calendar and country | `eom`, `excntry`; `eom` is the monthly key |
| Sample controls | `obs_main`, `common`, `exch_main`, `primary_sec` |
| Currency | `curcd`; `ret` is labeled total return in USD, `ret_local` total return in local currency |
| Return targets | `ret_exc` is labeled USD excess return; `ret_exc_lead1m` is labeled month t+1 USD excess return |
| Size and selected signals | `me`, `market_equity`, `size_grp`, `be_me`, `ret_12_1`, `beta_60m`, `age` |

Column labels establish the USD/local and current/lead distinctions, but not every numeric unit or transformation. For example, do not equate `me` and the characteristic named `market_equity` without checking their definitions. Read the current factor-detail resource for the sign of a characteristic before constructing high-minus-low returns. Keep raw values and any standardized versions separate.

## Bounded US stock-month recipe

```sql
SELECT eom AS date, id, permno, gvkey, excntry, curcd,
       obs_main, common, exch_main, primary_sec,
       me, size_grp, be_me, ret_12_1, beta_60m,
       ret, ret_local, ret_exc, ret_exc_lead1m
FROM contrib_global_factor.global_factor
WHERE permno = 14593
  AND excntry = 'USA'
  AND eom >= DATE '2024-01-01' AND eom < DATE '2024-02-01'
  AND common = 1 AND exch_main = 1 AND primary_sec = 1 AND obs_main = 1
ORDER BY date, id;
```

Fields were matched to the live catalog; only table-level planning access was probed. Confirm actual key uniqueness, row availability, and numeric scales before expanding. For non-US data, choose an observed `id` and country instead of requiring PERMNO. Do not interpret a missing PERMNO as a missing global stock.

The lead return belongs to the month after the characteristic observation. Record both formation and realization months when exporting a prediction dataset. When joining CRSP monthly observations, standardize the CRSP trading date to a calendar month key and retain both original dates. A new CCM join is not needed merely to attach the `gvkey` already present, but a study requiring a particular linking rule must verify how that supplied link was formed.
