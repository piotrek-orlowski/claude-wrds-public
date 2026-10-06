# LSEG products and research workflow

Checked 2026-10-05 against live metadata and
[WRDS LSEG product status](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/lseg/).
LSEG, Refinitiv, and Thomson Reuters labels coexist; `tr_*` does not mean a
retired database. Use the [catalog](../../wrds-catalog/SKILL.md) to inspect
all tables/columns and actual access outcomes.

## Product boundaries

| Product | Current underlying schema | Account discovery |
|---|---|---|
| IBES historical estimates | `tr_ibes` | Schema usage; 166 tables; September 2026 refresh |
| Worldscope | `tr_worldscope` | Schema usage; 23 tables; October 2026 refresh |
| Shared identities | `tr_common` | Schema usage; 30 tables; September 2026 refresh |
| IBES corporate/guidance/global aggregates/KPI | `tr_ibes_corporate`, `tr_ibes_guidance`, `tr_ibes_iga`, `tr_ibeskpi` | Separate products; underlying schema usage denied |
| Datastream | `tr_ds_equities`, `tr_ds_econ`, `tr_ds_comds`, `tr_ds_fut` | Underlying schema usage denied |
| Holdings/ownership/insiders | `tr_13f`, `tr_mutualfunds`, `tr_ownership`, `tr_insiders` | Underlying schema usage denied |
| SDC transactions | `tr_sdc_ma`, `tr_sdc_ni`, `tr_sdc_joint_ventures`, `tr_sdc_municipals`, `tr_sdc_private_equity` | Underlying schema usage denied |
| Other distinct modules | `tr_dealscan`, `tr_esg`, `tr_tass`, D&B products | Not accessible production modules in this account's discovery |

Some corresponding sample schemas are visible (`tr_sdc_samples`, `trsamp_*`,
and `ibessamp_kpi`); the catalog determines which. A sample must retain its
sample label and restricted coverage. The `sdc`, `tfn`, `ibescorp`, and
`ibeskpi` view grants are not full-product access. A planning-only probe does
not override an underlying guard or prove returned rows.

WRDS explicitly labels `tr_13f_archive` and `tr_mutualfunds_archive` uncorrected
archived data with no further updates. They are excluded. Do not infer that
the maintained `tr_13f`/`tr_mutualfunds` products are retired too.

## IBES: select the measurement first

| Need | Current table examples in `tr_ibes` |
|---|---|
| Analyst forecasts with linked actuals | `det_epsus`, `det_epsint`, `det_xepsus`, `det_xepsint` |
| Consensus snapshots | `statsum_epsus`, `statsum_epsint`, corresponding non-EPS tables |
| Actual releases | `act_epsus`, `act_epsint`, corresponding non-EPS tables |
| Unadjusted versions | `detu_*`, `statsumu_*`, `actu_*` |
| Normalized and restated measurements | `ndet*`, `nstatsum*`, `nact*`, `ract*`, `nract*` |
| Stopped/excluded estimates | `stop*`, `exc*`, and matching unadjusted/normalized variants |
| Recommendations/targets | `recddet`, `recdsum`, `recdstp`, `ptgdet`, `ptgsum` |
| Identity/adjustments/currency | `id`, `idsum`, `adj`, `adjsum`, `curr`, `hdxrati`, `hsxrat` |

These are different measurement families within the current delivery, not
interchangeable duplicates. Table comments in the catalog distinguish them.

Verified detail fields in `det_epsus`: `ticker,estimator,analys,fpi,measure,
fpedats,value,curr,pdf,anndats,anntims,actdats,acttims,revdats,revtims`, plus
linked actual values/dates. `fpi` is a forecast-horizon category; select the
fiscal period with `fpedats` as well. `pdf` concerns primary/diluted basis.
`curr`, actual currency, and report currency are separate fields.

Consensus `statsum_epsus` uses `statpers` for its snapshot, with `numest,
meanest,medest,stdev,highest,lowest,fpedats,fpi,measure` and actual-date fields.
A monthly consensus snapshot is not the last analyst forecast immediately
before an earnings release. Actuals `act_epsus` use `pends`, `pdicity`,
announcement/activation dates and `value`.

Before a forecast-error or surprise calculation:

1. Choose adjusted/unadjusted and normalized/reported definitions consistently
   for estimates and actuals; establish split/currency/primary-diluted basis.
2. Choose the information clock. Announced, activated, and reviewed times are
   different; retain original fields and compare only eligible forecasts.
3. Define the analyst/broker-period grain, stale-estimate cutoff, and stopped
   estimate treatment. Prove the keys before selecting the last eligible row.
4. Match measure, fiscal period, and actual release definition. Never use an
   embedded future actual as a predictor.
5. Report unmatched actuals, timing failures, duplicate forecasts, zero/missing
   consensus counts, and sensitivity to revisions on the pilot.

The [WRDS IBES notice](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-ibes/)
warns that broker/analyst codes changed substantially in October 2018 and may
be reassigned in other vintages; UBS Equities was also removed from detail
history. Preserve database vintage and do not assume these codes identify the
same researcher across saved downloads. `ticker` is IBES identity; `oftic` is
an exchange ticker. `id.sdates` supports identity history. Resolve CUSIP/SEDOL
meaning by region, and inspect the current WRDS CRSP-IBES link and dated
matching rules before linking to returns.

## Worldscope

Convenience modules are `wrds_ws_company`, `wrds_ws_funda`, `wrds_ws_fundq`,
`wrds_ws_ids`, `wrds_ws_segments`, `wrds_ws_pension`, `wrds_ws_stock`, and
`wrds_ws_stock_header`. Current-header stock information is not historical
membership. Lower-level `ws*data`, `wsfye`, `wscurr`, `wsfnote`, and text files
retain dictionary/footnote/frequency detail.

`wrds_ws_funda` has `code,year_,freq,seq` plus numbered `item*` fields. Use
`wsitem(number,name,frequency,datatype,units,table_,usbasis,nonusbasis,...)`
to identify the exact concept and units. Do not guess an item code or map a
numeric year straight to December 31. Preserve fiscal end, reporting period,
sequence/revision conventions, and currency before joining markets data.

Verified `wrds_ws_ids` fields include `code,freq,year_` and:

| Field | Metadata description |
|---|---|
| `item6035` | Worldscope identifier |
| `item6105` | Worldscope permanent ID |
| `item6038` | IBES ticker |
| `item5601` | Ticker |
| `item6006` | SEDOL |
| `item6008` | ISIN |
| `item6004` | CUSIP |

Identifiers may appear at multiple frequency/year rows. Resolve temporal
validity and uniqueness rather than joining every identifier row to every
accounting observation. Prototype one `code`, one item, and two reporting
periods; check units, sequences, revisions, currency, fiscal dates, and
coverage before expanding.

## Shared security identifiers

`tr_common` includes regional `secmstrx/gsecmstrx`, `secmapx/gsecmapx`,
`secventype`, identifier-change histories, and PermID organization/instrument/
quote tables. `permsecmapx` has `regcode,seccode,enttype,rank,entpermid,
startdate,enddate`. A numeric ID without its entity type and region is not a
complete join key. Interpret vendor/type codes from the dictionaries; do not
invent integer meanings or default to rank 1 without checking its semantics.

`permcusipdata`, `permisindata`, `permsedoldata`, and `permricdata` preserve
current and historical identifiers at different entity levels. Keep date
intervals and test one-to-many mappings. Datastream-Worldscope and
Dealscan-Worldscope linking products require their own access; shared identity
access does not imply the source databases or those links are subscribed.
