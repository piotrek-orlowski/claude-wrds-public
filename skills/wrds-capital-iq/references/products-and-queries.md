# Capital IQ modules and query design

Checked 2026-10-05 against live metadata and the
[WRDS S&P Global product listing](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sp-global-market-intelligence/).
The listed modules were refreshed in October 2026. Use the installed
[catalog](../../wrds-catalog/SKILL.md) for all table/column names, current
access outcomes, and alternate-delivery exclusions.

## Access and module map

| Module | Current schema | Snapshot |
|---|---|---|
| Common identities/helpers | `ciq_common` | 59 tables; schema usage |
| Capital structure | `ciq_capstrct` | 44 tables; schema usage |
| Key developments | `ciq_keydev` | 10 tables; schema usage |
| People intelligence | `ciq_pplintel` | 16 tables; schema usage |
| Transactions | `ciq_transactions` | 77 tables; schema usage |
| Ratings | `ciq_ratings` | Underlying schema usage denied |
| Transcripts | `ciq_transcripts` | Underlying schema usage denied |

`ciq` is a mixed view schema. Its ratings/transcript views do not override
product permissions. `ciqsamp_*` provides restricted samples; never label a
sample result as the requested full universe. Follow observed access guards;
do not bypass a denied alias through a base table. `_old` delivery copies are
outside current recipes. WRDS date extrema can include sentinel dates.

## Entity links

Verified core layouts:

- `ciqcompany`: `companyid,companyname,companytypeid,companystatustypeid`.
- `ciqsecurity`: `securityid,companyid,securitystartdate,securityenddate,
  securitysubtypeid,primaryflag`.
- `ciqtradingitem`: `tradingitemid,securityid,tickersymbol,exchangeid,
  currencyid,tradingitemstatusid,primaryflag`.
- `wrds_gvkey`: `companyid,gvkey,companyname,startdate,enddate,primaryflag`.
- `wrds_cusip`: `companyid,cusip,companyname,startdate,enddate,primaryflag`.

Join company to security with `companyid`, then security to listing with
`securityid`. Tickers belong to listings and can be reused. To link Compustat,
evaluate `wrds_gvkey` at the chosen observation/formation date, keep GVKEY as
text, and inspect overlapping links. `wrds_cik`, `wrds_isin`, `wrds_ticker`,
`wrds_ciqsymbol`, `ciqgvkeyiid`, and symbol-type dictionaries cover other IDs;
inspect their exact grain before using them. Company relationships and index
constituents are additional one-to-many modules, not static company attributes.

## Capital structure

Start with `wrds_debt`, `wrds_equity`, or `wrds_summary` for a bounded pilot,
then use normalized tables if exact filing-vintage reconstruction is required.
`wrds_debt` exposes `companyid,periodenddate,filingdate,componentid,
financialcollectionid,dataitemid,dataitemvalue,unittypeid,issuedcurrencyid,
financialinstanceid`, component types, and restatement/latest flags.

The normalized path is `ciqfinperiod` to `ciqfininstance` through
`financialperiodid`, then `ciqfininstancetocollection` and collection data.
`ciqfinperiod` carries company/fiscal/calendar period identities;
`ciqfininstance` carries period end, filing date, currency, form, accession,
and restatement flags. Collection, debt/equity component, and data-item rows
can multiply an instance. Do not sum every `dataitemvalue`: summary, component,
and repeated filing values can overlap. Read `ciqdataitem`, `ciqfinunittype`,
capital-structure type dictionaries, and collection link fields first.

Prototype one company, two period ends, and one documented item. Count
financial instances per period and components per item. Preserve amendments
and compare filing-date availability with the research cutoff before choosing
one instance. Distinguish maturity ranges from exact maturity dates and
reported interest rates from benchmark spreads.

## Key developments

`wrds_keydev` includes `keydevid,companyid,keydeveventtypeid,
keydevtoobjectroletypeid,headline,situation,announcedate,announcetime,
announcedatetimezone,announceddateutc,entereddateutc,lastmodifieddateutc,
mostimportantdateutc,speffectivedate,sptodate,sourcetypename`.

Keep the exact spelling `announceddateutc`. Use the supplied UTC field when
appropriate instead of adding an assumed timezone to a local time. The
announcement, vendor entry, modification, and most-important dates represent
different clocks. An event may relate to multiple companies or categories;
choose an event-company-role grain before joining stock returns. Use
`ciqkeydevtoobjecttoeventtype` and role/category dictionaries to interpret that
relationship. `wrds_keydev_div` is the dividend/split convenience route.

Pilot one company and one event class for a month. Inspect duplicate event
IDs, missing times, time ordering, modifications, and weekend announcements;
retain source timestamps and a declared trading-session mapping.

## People and compensation

`wrds_professional` has `companyid,personid,proid,profunctionid`, role titles,
start/end day/month/year components, rank, and current/board/executive flags.
Partial dates are not exact dates: do not fabricate a day when only a year is
known. A person can hold simultaneous roles at several companies.

Use `wrds_compensation`, `wrds_compensationdetails`, `ciqcompensation*`, and
type dictionaries for pay. First establish person-company-period-component
keys and units, then aggregate a specified set of components. `ciqperson` and
`ciqpersonbiography` are identity/descriptive sources; they do not establish
historical role tenure by themselves.

## Transactions

`wrds_transactions` exposes `transactionid`, target and related-company IDs,
relationship fields, `lateststatus`, `lateststatusdatetime`, `announceddate`,
`closingdate`, `canceleddate`, `transactionsize`, `transsizeusd`, and
`localcurrency`. The many columns and relationships mean `transactionid`
alone is not a guaranteed row key in a convenience extract.

Choose target/acquirer/investor roles, deal type, and announcement/completion
sample rules first. Keep canceled and pending deals if the design calls for
them; filtering to current completed status can bias an announcement sample.
Advisors, considerations, conditions, and features live in separate
`wrds_trans_*` tables and can create cross products when joined together.
Aggregate each child table at its intended grain before joining.

Offerings have their own `wrds_offerings*` routes for advisors, features,
proceeds, registration, and relationships. Use transaction/data-item/type
dictionaries to interpret fields. Verify currency conversion dates and value
units before comparing local transaction size with USD values.
