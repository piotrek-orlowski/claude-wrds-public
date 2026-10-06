# WRDS provider and product evidence

Retrieved **2026-10-05** through public web search and primary provider pages.
This is a source directory for reconciling the live catalog, not an entitlement
list. No WRDS SQL, credential access, private web login, research-data download,
or installation was performed for this document.

Product/schema names below are WRDS website labels. They may name a product
group or underlying schema rather than the convenient SQL alias. Confirm the
actual namespace, columns, privileges, and bounded sample in the live inventory.
An update date describes the website's product record; it does not establish
the newest observation in each table. A product's long history does not make it
retired, and an old update without a retirement label does not prove retirement.

## Directories and identity mapping

| ID / scope | Primary title and URL | Retrieved | Establishes | Limits |
|---|---|---|---|---|
| DIR-1 / all vendors | [WRDS Data Vendors](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/) | 2026-10-05 | Provider directory with product pages, dictionary links, and vendor identity; includes LSEG, LSEG Mergent, Ideagen Audit Analytics, FINRA, and Federal Reserve Board. | Does not establish this account's access; omitted entries need not be unavailable. |
| DIR-2 / WRDS-created products | [WRDS vendor/product page](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-wrds/) | 2026-10-05 | Product labels and dictionary links for WRDS suites, contributed data, linking products, and public data. | Website product ranges can contain sentinel or anomalous dates; do not present them as validated coverage. |
| LINK-1 / cross-product | [WRDS Database Linking Tool](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/database-linking-tool/) | 2026-10-05 | Routes CIQ company IDs through GVKEY, Audit Analytics through CIK/Compustat, bonds through a bond–CRSP link, and IBES through its CRSP link/security mapping. | A documented route does not prove unique matches or current link coverage. Inspect dates, key direction, and quality fields. |
| LINK-2 / visual directory | [WRDS Company Database Linking Matrix](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/) | 2026-10-05 | Alternative navigation for linking notes and notebooks. | Linked instructional content can require login; the matrix is not a field dictionary. |

The directory's “Often Paired With” lists are recommendations, not dependency
or access evidence. Its “Identifiers” tags are incomplete: a missing tag does
not establish that a table has no identifiers. Examples of website ranges
extending to years 2924, 4000, or 9999 demonstrate why observation coverage must
be checked independently.

## Fama–French and JKP Global Factor Data

| ID / scope | Primary title and URL | Retrieved | Establishes | Limits |
|---|---|---|---|---|
| FF-1 / WRDS product | [Fama–French Portfolios & Factors](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/fama-french-portfolios-factors/) | 2026-10-05 | WRDS product code `ff_all`; page reports daily updates and last update 2026-10-03. | Inspect aliases and individual factor tables; the page does not prove local access or return scaling. |
| FF-2 / methodology version | [Kenneth French — Changes in CRSP Data](https://mba.tuck.dartmouth.edu/pages/Faculty/ken.french/Data_Library/changes_crsp.html) | 2026-10-05 | US research returns switched to CRSP CIZ starting with the January 2025 release; the legacy format ended with December 2024. | Preserve extract vintage; a historical observation date alone does not identify the construction version. |
| FF-3 / legacy archive | [US Historical Research Returns as of December 2024](https://mba.tuck.dartmouth.edu/pages/faculty/Ken.french/data_library_202412_archive.html) | 2026-10-05 | Explicit frozen legacy-format archive, distinct from ongoing research-return releases. | Replication source, not the default current factor series. |
| JKP-1 / WRDS usage | [JKP WRDS Data Guide](https://jkpfactors.com/jkp-wrds-guide) | 2026-10-05 | Documents `contrib.global_factor`, `id`, `eom`, `excntry`, `gvkey`, `permno`; screens `common`, `exch_main`, `primary_sec`, and `obs_main`; identifies `ret_exc_lead1m` as the next-month return. | The guide's Python authentication and unrestricted extraction examples are not this repository's execution policy. Use direct psql and bounded dates. Verify the actual catalog/vintage. |
| JKP-2 / distribution | [Global Factor Data — Data Download](https://jkpfactors.com/data) | 2026-10-05 | Separates public factor/portfolio returns from monthly stock characteristics on WRDS; offers factor mappings, NYSE cutoffs, and return cutoffs. | Public factor return files and stock-characteristic tables are different products. Access to one does not imply another. |
| JKP-3 / maintained implementation | [bkelly-lab/jkp-data](https://github.com/bkelly-lab/jkp-data) | 2026-10-05 | Author-maintained Python implementation, data changelog and documentation; recommends it for future work while retaining the original SAS/R codebase. | A code checkout is not the WRDS table's release/version. Do not rebuild or download the full pipeline merely to document an available table. |
| JKP-4 / manual | [Global Factor Data Documentation](https://jkpfactors-data.s3.amazonaws.com/documents/Documentation.pdf) | 2026-10-05 | Current provider-linked manual; contents include identifier variables, portfolio construction, accounting characteristics, and factor definitions. | Located as a manual, not an academic-paper review. Read relevant definitions when a particular variable is implemented; no wholesale methodology verification here. |

The `www.jkpfactors.com` guide initially returned 502; the canonical non-`www`
link above was fetched successfully. The current site links documentation from
`jkpfactors-data.s3.amazonaws.com`; old references can point to a different bucket.

## Corporate bonds: distinguish raw, cleaned, and reference data

| ID / scope | Primary title and URL | Retrieved | Establishes | Limits |
|---|---|---|---|---|
| TRACE-1 / WRDS products | [FINRA on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/finra/) | 2026-10-05 | Separate `trace_standard` and `trace_enhanced` products; page reports quarterly updates, last update 2026-06-18. | Does not establish access, SQL aliases, or cleaning rules. |
| TRACE-2 / product distinctions | [FINRA Historic Data Information](https://www.finra.org/filing-reporting/trace/historic-academic-data) | 2026-10-05 | Enhanced historical trades include uncapped size and additional trade attributes; Academic Corporate Bond TRACE is a distinct delayed product with masked dealer identity. Lists pre/post-2012 file-layout links and CUSIP/non-CUSIP versions. | Provider release delays and licensing differ by product; do not infer that a WRDS table is the academic dealer-identified product. |
| TRACE-3 / field manual | [Enhanced Historic Time and Sales Trade Record File Layout](https://www.finra.org/sites/default/files/AppSupportDoc/p353157.pdf) | 2026-10-05 | Post-2012 native layout; distinguishes TRACE symbol, bond CUSIP, trade status, and reporting/transaction fields. | Native-file names and encodings need mapping to WRDS columns. Corrections and reversals require an explicit treatment. |
| BOND-1 / WRDS cleaned data | [WRDS Bond Returns](https://wrds-www.wharton.upenn.edu/pages/grid-items/wrds-bond-returns/) | 2026-10-05 | WRDS-created cleaned Standard/Enhanced TRACE transactions, monthly price/return/coupon/yield data, and bond/equity mapping. | Distinct from Dickerson contributed panels and raw TRACE. The overview links methodology; do not assume identical filters or returns across products. |
| BOND-2 / Dickerson contribution | [Alex Dickerson — data links](https://www.alexdickerson.com/) | 2026-10-05 | Author explicitly links separate monthly and daily WRDS contributed datasets. | Author announcements do not establish the accessible table's latest date or field list. |
| BOND-3 / public subset | [Open Source Bond Asset Pricing — Data](https://openbondassetpricing.com/data/) | 2026-10-05 | Public daily data combines Enhanced, Standard, and 144A TRACE; proprietary fields such as GVKEY and ratings are excluded from public downloads. Links dictionaries and stage reports. | The public file is not a field-for-field substitute for licensed WRDS data. |
| BOND-4 / maintained definitions | [Alexander-M-Dickerson/trace-data-pipeline](https://github.com/Alexander-M-Dickerson/trace-data-pipeline) | 2026-10-05 | Author pipeline with stage dictionaries for transaction cleaning, daily analytics, and monthly panels. | Documentation source only in this task. Its remote execution instructions do not override this repository's TAQ-only SSH rule. Pin a version before using definitions as a table contract. |
| BOND-5 / previous code | [TRACE-corporate-bond-processing](https://github.com/Alexander-M-Dickerson/TRACE-corporate-bond-processing) | 2026-10-05 | GitHub marks the former author repository as archived; it links newer data resources. | Preserve for historical reproduction rather than treating its scripts as current default instructions. |
| FISD-1 / reference and transaction products | [LSEG Mergent on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/lseg-mergent/) | 2026-10-05 | FISD supplies debt-issue/issuer information and insurance transactions. WRDS labels `fisd_common`, `fisd_fisd`, and `fisd_naic`; update recorded 2026-08-13. `fisdsamp_all` is a sample. | Do not confuse issue-reference data, NAIC transactions, and TRACE trades. Verify issue/issuer key columns from the actual table dictionary. |
| FISD-2 / WRDS manual | [FISD Merged Datasets Overview](https://wrds-www.wharton.upenn.edu/pages/support/manuals-and-overviews/mergent-fisd/fisd/fisd-merged-datasets-overview/) | 2026-10-05 | Official overview destination linked by WRDS. | Public request redirects to login; contents were not inspected. |

## Analyst estimates, ownership, and corporate information

| ID / scope | Primary title and URL | Retrieved | Establishes | Limits |
|---|---|---|---|---|
| LSEG-1 / current families | [LSEG on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/lseg/) | 2026-10-05 | Product codes include `tr_ibes`, `tr_ibeskpi`, `tr_ownership`, `tr_insiders`, `tr_13f`, `tr_mutualfunds`, `tr_common`, and Datastream/SDC modules. | Product grouping is not the SQL alias, row grain, or entitlement. |
| LSEG-2 / ownership version boundary | [LSEG on WRDS — archive and holdings sections](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/lseg/) | 2026-10-05 | Explicitly marks `tr_13f_archive` and `tr_mutualfunds_archive` as uncorrected/corrupted archives no longer updated; current holdings entries have September 2026 updates. | Exclude archives from current default routing even if queryable; retain their identity for intentional replication. |
| IBES-1 / product scope | [WRDS I/B/E/S Overview](https://wrds-www.wharton.upenn.edu/pages/grid-items/overview-ibes-demo/) | 2026-10-05 | Distinguishes analyst-level and summary forecasts, recommendations, Global Aggregates, KPI, and management Guidance. | It does not define forecast-period flags, adjustment basis, timestamp fields, or analyst IDs. Those need the exact table/manual. |
| CIQ-1 / current modules | [S&P Global Market Intelligence on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sp-global-market-intelligence/) | 2026-10-05 | Separates `ciq_capstrct`, `ciq_common`, `ciq_keydev`, `ciq_pplintel`, `ciq_ratings`, `ciq_transactions`, and `ciq_transcripts`; October 2026 updates shown. | Verify company/security/person/transcript identifiers and their relationships by module; no universal company-row key. |
| CIQ-2 / retired products | [S&P Global Market Intelligence — legacy sections](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sp-global-market-intelligence/) | 2026-10-05 | Explicit legacy labels for S&P Filing Dates (`comp_filings`) and older S&P Ratings. | A similarly named current CIQ ratings product is not necessarily a drop-in replacement. |
| AA-1 / audit products | [Ideagen Audit Analytics on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/audit-analytics-and-oia-other-independent-audits/) | 2026-10-05 | Splits `audit_acct_os`, `audit_audit_comp`, `audit_common`, `audit_corp_legal`, `audit_esg_funds`, and regional modules; distinguishes `auditsmp_all` trial. | Product-page ranges are not credible observation bounds by themselves. Select event/filer grain and validate CIK-to-company links. |
| BOARD-1 / product generations | [BoardEx on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/boardex/) | 2026-10-05 | Lists current BoardEx and Altrata Executive & Company regional products, each with separate sample/trial offerings. | Similar product purpose does not establish interchangeable person/organization IDs, column layouts, or account access. |
| BVD-1 / current and legacy | [Bureau van Dijk on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/bureau-van-dijk-bvd/) | 2026-10-05 | Explicitly labels Amadeus size products/trial as legacy and no longer updated; Orbis, Bank Focus and Osiris have current annual product updates. | An updating product can still be inaccessible to this account. Size-segment combinations and sample schemas require exact table mapping. |

For IBES, the WRDS page reports `tr_ibes` updated 2026-09-12 and KPI updated
2026-09-17. For holdings it reports `tr_13f` updated 2026-09-14 and
`tr_mutualfunds` updated 2026-09-08. These are dated website observations, not
promises about underlying tables or current access.

## TAQ product lifecycle versus annual partitions

| ID / scope | Primary title and URL | Retrieved | Establishes | Limits |
|---|---|---|---|---|
| TAQ-1 / WRDS annual cards | [NYSE Trade and Quote on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/nyse-trade-and-quote-taq/) | 2026-10-05 | Exact `taqm_YYYY` annual-product labels; many completed years are marked no longer updated. | A closed annual partition's label alone does not establish retirement of the parent Daily TAQ product. |
| TAQ-2 / ongoing product | [NYSE Daily TAQ](https://www.nyse.com/data-products/catalog/daily-taq) | 2026-10-05 | Ongoing daily consolidated trades/quotes product with historical data. | NYSE native delivery is distinct from account-specific WRDS availability and SAS layout. |
| TAQ-3 / era-specific manuals | [NYSE technical documents](https://www.nyse.com/market-data/technical-documents) | 2026-10-05 | Current June 2026 v4.3 specification plus historical Daily TAQ versions. | Select the version for the file era; display precision and source timestamp accuracy differ. |
| TAQ-4 / WRDS product distinction | [Daily TAQ-to-CRSP linking manual](https://wrds-www.wharton.upenn.edu/documents/1336/NYSE_Daily_TAQ_to_CRSP_Linking_BPNFjWm.pdf) | 2026-10-05 | Technical manual explicitly distinguishes Monthly TAQ (1993–2014) from Daily TAQ (2003 onward). | Dated linking manual, not current link coverage or a guarantee that old annual files continue receiving revisions. |

Catalog policy therefore treats the observed `taqm_2003`–`taqm_2026` partitions
as historical years of a maintained Daily TAQ product, separately from legacy
monthly TAQ/NASTRAQ/ISSM and from `_old`/`_new` alternate versions. This is an
explicit interpretation of the combined primary evidence, not a rewrite of the
website's frozen-year labels. SAS metadata and a bounded SAS prototype are
required for actual TAQ work; PostgreSQL TAQ metadata remains discovery only.

## Macro and public-source definitions

| ID / scope | Primary title and URL | Retrieved | Establishes | Limits |
|---|---|---|---|---|
| MACRO-1 / WRDS rates | [Federal Reserve Board on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-federal-reserve-board/) | 2026-10-05 | WRDS product `frb_all`; page lists irregular updates and last update 2025-02-19. | Not labeled retired. Verify each series' most recent date instead of calling it current or discontinued from this timestamp alone. |
| MACRO-2 / contributed macro | [Macro Finance Society on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-macro-finance-society/) | 2026-10-05 | Product `macrofin_comm_trade`; page says no scheduled updates, last update 2020-02-19. | A fixed research dataset can remain usable; no claim of ongoing coverage or retirement follows. |
| MACRO-3 / official interest rates | [Federal Reserve H.15 Data Download](https://www.federalreserve.gov/datadownload/Choose.aspx?rel=H15) | 2026-10-05 | Official H.15 release/source navigation for Selected Interest Rates. | External definition/reference source; does not prove the same series or vintage is hosted in WRDS. |
| MACRO-4 / vintage semantics | [FRED API — Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) | 2026-10-05 | Defines information-vintage date bounds separately from observation periods. | Date-level vintage metadata is not a subsecond release timestamp; do not assume a WRDS macro table preserves vintages. |
| MACRO-5 / observation schema | [FRED API — Series Observations](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) | 2026-10-05 | Documents series identifiers, observation dates, values, real-time bounds, units and transformation controls. | Reference only; no FRED API request or key use performed. |
| PUBLIC-1 / WRDS dictionary | [Publicly Available Data](https://wrds-www.wharton.upenn.edu/data-dictionary/public_all/) | 2026-10-05 | Verified WRDS dictionary destination for the public-data grouping. | Redirected to login; membership and fields must come from live inventory/authorized documentation. |

## Verified dictionary destinations with gated contents

The following destinations were reached through official links but redirected
to WRDS login. They are useful follow-up locations, not inspected dictionaries:

- [Fama–French `ff_all`](https://wrds-www.wharton.upenn.edu/data-dictionary/ff_all/)
- [Dickerson corporate bonds `contrib_bond_dickerson`](https://wrds-www.wharton.upenn.edu/data-dictionary/contrib_bond_dickerson/)
- [Public data `public_all`](https://wrds-www.wharton.upenn.edu/data-dictionary/public_all/)
- [FISD overview](https://wrds-www.wharton.upenn.edu/pages/support/manuals-and-overviews/mergent-fisd/fisd/fisd-merged-datasets-overview/)

## Applying this evidence to the live inventory

1. Preserve both the observed SQL name and the matching website product label.
   A label match is a candidate mapping until supported by metadata or dependencies.
2. Distinguish current/updating, explicitly frozen/archived, sample/trial,
   historical unscheduled, and unresolved products. Keep the evidence URL beside
   the classification; do not classify by name or last-update age alone.
3. Use provider manuals for units, field meanings, identifier scopes, and version
   changes. Use live metadata and bounded reads for columns and actual access.
4. Record unavailable documentation and access failures rather than replacing
   them with guessed schema knowledge. Authentication success and catalog visibility
   do not prove every table can be read.
5. For joined panels, retain security/issuer/manager/analyst/series identifiers
   separately. Source observation date, public-information date, vendor vintage,
   and WRDS load date answer different questions.

No academic paper was opened or summarized for these findings. Manuals, product
pages, and author-maintained data/code documentation supply the evidence.
