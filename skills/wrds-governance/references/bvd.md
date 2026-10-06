# Bureau van Dijk: company identity, ownership, and financial statements

## Choose the product and population

The [WRDS BvD directory](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/bureau-van-dijk-bvd/),
retrieved 2026-10-05, explicitly labels Amadeus size products and its trial
**legacy, no longer updated**. Orbis size products, Bank Focus, and Osiris have
current annual product updates. A retired default and a currently inaccessible
product are different conditions.

The local 2026-10-05 permission/planning inventory accepted 232 `bvd` alias
relations: 204 `ob_*`, 27 `bvdbankf_*`, and the Orbis query-variable relation.
It identified 104 others, including Amadeus and Osiris, as guard-denied.
All 18 `bvdsamp` relations were accepted as samples; three Amadeus trial
relations are legacy, leaving 15 in current-default catalog coverage.
A planning probe does not
verify observation coverage. Refresh each exact table through `wrds-catalog`.

Orbis `_l`, `_m`, `_s`, `_lm`, and `_lms` forms have different size/population
scopes; inspect the relation comment and underlying product. `_lms` already
covers all-size products where documented: appending `_l`, `_m`, and `_s` to it
can duplicate firms. `bvdsamp.bvdbankf_bank` and
`bvdsamp.bvdbankf_financials` are trial table names; the current full Bank Focus
product uses different tables such as `bvd.bvdbankf_identifiers`,
`bvd.bvdbankf_contact_info`, `bvd.bvdbankf_global_standard_format`, and
`bvd.bvdbankf_global_format_ratios`. Do not extrapolate old sample schemas.

In the current `bvd.bvdbankf_global_standard_format`, the entity key is
`bvd_id_number` (`varchar(50)`), with `bvd_bank_index_number` and
`consolidation_code`; **`closing_date` is `varchar(8)`**, unlike Orbis's date-typed
`closdate`. Inspect the actual representation before parsing or comparing dates.
Join current Bank Focus identifiers using `bvd_id_number` after checking the
statement/consolidation grain; do not mechanically reuse an Orbis `bvdid` query.
Retain the full Bank Focus fields `number_months`, `fiscal_year`, `quarter_year`,
`original_unit`, `original_currency`, `usd_exchange_rate`, and
`eur_exchange_rate` when validating periods, scale, and currency basis. These
names differ from the adjacent Orbis `nr_months`/`orig_units` examples; inspect
their exact types and code definitions in the selected Bank Focus table.

## Orbis identity and financial panels

`bvd.ob_w_company_id_table_l` and `_lms` contain text `bvdid`, `lei_lei`,
`sd_ticker`, `sd_isin`, company-name and country fields, listing status, and
historical-name/status dates. Preserve `bvdid` as text. A security identifier
can have multiple securities per firm and can change over time; use dated
cross-product links through `wrds-linking` rather than ticker alone.

`bvd.ob_w_ind_g_fins_cfl_usd_l` is a current observed industrial-company
financial route. Its fields include:

| Field | Observed type/comment and use |
|---|---|
| `bvdid` | `varchar(50)`, BvD ID; entity identifier |
| `conscode` | `varchar(5)`, consolidation code; retain statement scope |
| `closdate` | date, closing date; fiscal period end |
| `filing_type`, `accpractice`, `audstatus`, `source` | Statement basis/provenance; inspect exact code definitions |
| `nr_months` | `varchar(2)`, number of months; period length is not safely assumed numeric/12 |
| `orig_units`, `orig_currency` | Original units/currency fields; retain when comparing converted values |
| `exchrate` | double precision, exchange rate from original currency |
| `toas`, `opre`, `turn`, `pl` and other measures | Retrieve current column comments for each requested measure before assigning economic labels |

Start with one `bvdid` and one fiscal year. Identify multiple consolidations,
filing types, closing dates, and annual versus interim periods before choosing
the panel key. Do not collapse them by arbitrary maximum values. Select the
appropriate industrial, bank, or insurance statement family and currency
variant explicitly. Product currency labels do not by themselves establish
measurement scale. Fiscal closing date is not public filing availability.

## Ownership edges and code traps

Actual column comments/types from 2026-10-05 identify these fields:

| Table/edge | Owner or subsidiary identity | Holdings | Information date |
|---|---|---|---|
| `bvd.ob_all_cur_shh_1st_level_l` | Investee `bvdid`; shareholder `_9006` (BvD ID), `_9001` (name), `_9015` (type) | `_9009` direct %, `_9010` total %, both `varchar(7)` | `_9033` date, `_9021` source |
| `bvd.ob_all_subs_first_level_l` | Parent `bvdid`; subsidiary `_9305` (BvD ID), `_9300` (name), `_9314` (type) | `_9308` direct %, `_9309` total %, both `varchar(7)` | `_9332` date, `_9320` source |

Ownership percentages are strings: preserve raw values and separate parseable
numeric values from special tokens, missing values, and bounds. Decode tokens
from the relevant manual before imposing majority-control thresholds. Direct
and total percentages are different measures; do not add both as independent
stakes. First-level records are not a ready-made ultimate-owner graph.

Despite its name, `shareholders_isinwocoformatted` is a three-character
**WorldCompliance same/similar-name indicator**, according to the actual column
comment. It is not a shareholder ISIN. The subsidiary counterpart has the same
trap. For security links use verified identifier fields and tables.

These tables describe **current** first-level ownership and include information
dates. Those dates do not turn a current snapshot into historical ownership
at arbitrary past dates. Preserve extract date and source information date;
request a genuine historical product/vintage when the analysis requires it.
For graph work, retain edge direction, entity type, percentage basis, and date;
check duplicate edges, cycles, missing owners, and incompatible scopes before
traversing control chains.

## Source limits

The [official Orbis overview](https://wrds-www.wharton.upenn.edu/pages/support/manuals-and-overviews/bureau-van-dijk/orbis/wrds-overview-bvd-orbis-database/)
redirected to login on 2026-10-05. Live column metadata verifies the field labels
above, but not every ownership token, consolidation-code rule, or historical
retention policy. Keep unresolved meanings explicit. The
[WRDS linking tool](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/database-linking-tool/)
describes BvD security linking through ISIN/CUSIP/SEDOL; it does not supply
one-to-one company mappings or validate their historical intervals.
