# Current-product evidence: CRSP, Compustat, OptionMetrics

Research date: 2026-10-05. This note combines official provider/WRDS public
documentation with this account's metadata discovery. It records product
lifecycle separately from access. It does not claim to have extracted rows
from every table or verified every historical data unit.

Machine-readable decisions: [current-product-overrides.json](current-product-overrides.json).
Each rule names a schema and explicit tables, status, replacement, source URLs,
reason, and metadata provenance. `superseded_copy` identifies an alternate
delivery with a documented current endpoint without asserting provider
retirement. `unresolved` is not equivalent to `current` or `retired`.
Dependencies propagate base-table decisions to
aliases; schema grants or `LIMIT 0` alone cannot establish row access.

## Source register

| Source | Date/status evidence | Use |
|---|---|---|
| [WRDS: Changes to CRSP Data](https://wrds-www.wharton.upenn.edu/pages/data-announcements/changes-to-crsp-data/) | Checked 2026-10-05; final SIZ period December 2024, WRDS final delivery February 2025 | SIZ exclusion; CIZ current |
| [WRDS Research Webinar: CRSP CIZ Data](https://wrds-www.wharton.upenn.edu/documents/2084/Webinar.pdf) | May 14, 2025; slide 27 explicit table mapping | DSF/MSF, StockNames/DSE/MSE, DSI/MSI replacements |
| [CRSP Cross Reference Guide](https://www.crsp.org/wp-content/uploads/guides/CRSP_Cross_Reference_Guide_1.0_to_2.0.pdf) | Public search index, May 2026 crawl; direct provider download currently 404 | SIZ SFZ daily/monthly index families map to CIZ; record broken-link limitation |
| [CRSP Flat File Format 1.0 guide](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-guide-flat-file-format-1-0/) | Checked 2026-10-05 through public search index; page 1 identifies SAZ and its file families | Identify the 32 recorded SAZ/SAZ legacy tables as the pre-CIZ stock format |
| [Morningstar CRSP Historical Indexes guide](https://indexes.morningstar.com/docs/guide/crsp-historical-indexes-guide?isRdp=true), [readable PDF](https://indexes.morningstar.com/api/docs/6a67e50d879300a48c6aa86a) | July 2026; read 2026-10-05; pp. 37–38 and 46–55 | Maintained IFZ/SFZ delivery; correct earlier blanket retirement inference |
| [WRDS CRSP product listing](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/center-for-research-in-security-prices-crsp/) | Checked 2026-10-05; annual stocks July 2026, mutual funds August 2026, Treasury/CCM/Ziman 2026 deliveries | Maintained product boundaries; cadence differs from observation frequency |
| [CRSP September 2014 Treasury release notes](https://www.crsp.org/crsp_pdf/september-2014-monthlyquarterly-release-notes/) | September 2014; December 2014 specified as final legacy release | Retired legacy Treasury formats |
| [CRSP Monthly US Treasury Guide](https://wrds-www.wharton.upenn.edu/documents/409/CRSP_Monthly_US_Treasury_Guide.pdf) | November 30, 2010; readable PDF, printed pages 24–25 list SAS filenames | Exact names for all 33 remaining legacy Treasury tables in each delivery schema |
| [CRSP Treasury guide](https://www.crsp.org/wp-content/uploads/guides/CRSP_US_Treasury_Database_Guide_for_SAS_ASCII_EXCEL_R.pdf) | Public search-indexed provider guide; direct fetch failed during this review | Current TFZ families and legacy BM/BX/riskfree mapping; monthly RF yield units |
| [WRDS S&P Global product listing](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sp-global-market-intelligence/) | Checked 2026-10-05; daily/global/bank/segments/snapshot/PIT/PH October 2026 refreshes; ExecuComp October 4 | Separate maintained products; do not exclude historical/snapshot names |
| [WRDS Introduction to ExecuComp](https://wrds-www.wharton.upenn.edu/pages/classroom/introduction-execucomp/) | Checked 2026-10-05; public introduction notes 2006 standards transition | Historical format comparability |
| [WRDS OptionMetrics product listing](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics/) | Checked 2026-10-05; IvyDB US annual delivery June 6, 2026; Europe listing older | Current US endpoint and delivery cadence; Europe lifecycle not inferred from stale refresh |
| [OptionMetrics data products](https://optionmetrics.com/data-products/) | Checked 2026-10-05; IvyDB US starts January 1996 and provider updates daily | Product history vs WRDS delivery |
| [OptionMetrics IvyDB US 7.0 / ETF 5.0 release](https://optionmetrics.com/news/optionmetrics-releases-ivydb-us-7-0-and-ivydb-etf-5-0/) | February 19, 2026 | Borrow-rate-aware analytics; current BRFitted family context |
| [OptionMetrics IvyDB US flyer](https://optionmetrics.com/wp-content/uploads/2024/03/OM_IvyDB-US_Flyer_WEB_REV.pdf) | 2024 publication, checked 2026-10-05 | Correct inherited fixed 100-step pricing claim; current implementation still needs version-specific documentation |

Detailed WRDS transition/manual links redirect to login. Public primary sources
and catalog comments are used here; no credentials were read. Search-indexed
provider passages support limited mappings, not a claim that inaccessible
manuals were reviewed in full. Future refreshes should replace broken URLs
with current official locations.

## Metadata evidence

Inputs are `catalog/discovery/schemas.jsonl`, `relations.jsonl.gz`,
`dependencies.jsonl.gz`, and `column-layouts.jsonl.gz`. Relation OIDs connect
columns to tables. Table comments record delivery dates; a comment alone is
corroboration, not a universal lifecycle rule. Access probes and observed view
guards belong to the independent inventory audit.

CRSP's annual stock schema contains both formats. The comments for recognized
SIZ tables retain February 2025 delivery dates, while CIZ stock/metadata and
index files carry 2026 dates. Together with explicit official mappings this
supports retiring the old formats. `dsi`/`msi` were not classified by field
spelling. The Format 1.0 guide explicitly identifies SAZ as the stock-only
flat-file set. Its named families and the recorded layouts identify all 32
`saz*` tables, including alternate `_legacy` copies, as the retired pre-CIZ
stock delivery.

The July 2026 Historical Indexes guide expressly continues standalone IFZ and
documents four SFZ files. The override retains 40 exact IFZ filenames and those
four SFZ endpoints as current, including `dsp500p`/`msp500p`. Preferring CIZ is
not a lifecycle decision. Earlier blanket retirement inference for these
index files is withdrawn. Another 41 assignment/alternate/helper endpoints
remain unresolved. The three Select Treasury endpoints also remain unresolved:
their fields resemble the guide's ASCII specification, but their WRDS delivery
mapping is unverified; CTI is not an interchangeable substitute. Table freshness
was not checked. This separates the explicit SIZ withdrawal from maintained
index modules despite overlapping terminology.

The 2010 monthly Treasury guide lists every remaining supplemental filename:
the MB calendar/master/cross-section files, bond portfolios, Fama-Bliss, and
bid/ask/average term-structure panels. Together with the 2014 retirement notice,
this resolves 33 tables in each of the annual and quarterly Treasury schemas.
Other unresolved CRSP/Compustat entries are `stock_qvards`, five sample
CCM/helper files, and the Global placeholder below.

The current mutual-fund product has 29 tables; `fund_hdr_hist` is retained
history inside that product. Current TFZ files include RF/RF2 and TS/TS2;
original series are not obsolete just because newer series coexist. Annual
and quarterly Treasury products overlap and must not be concatenated.

Compustat current access candidates cover North America (206 tables), Global
(125), and ExecuComp (15). The `comp` alias also advertises products whose
underlying schemas deny usage. Snapshot, PIT, preliminary history, bank, and
historical segments remain maintained distinct products, not legacy replicas.
ExecuComp's `codirfin`, `ltawdtab`, and `stgrttab` retain old-period layouts
within the current product. Global's placeholder `g_tmptable_pkg6775_tbl5551`
has unresolved purpose.

IvyDB US has 402 current base tables: 13 annual families spanning 1996-2025 and
12 nonpartitioned tables. Five BRFitted families accompany standard families.
The 28 `optionm.distrprojdYYYY` aliases are stale: their dependencies name the
old base, and their privilege predicates refer to nonexistent current tables.
No replacement was verified. Current underlying distribution history is a
different concept and must not be substituted silently.

Alternate `_old` schemas have no verified public retention policy. They are
excluded from current recipes and tagged `superseded_copy`, with the documented
current endpoint as replacement. A year partition or history suffix by itself
does not trigger this rule. The CRSP sample product is also split: CIZ samples
remain current with restricted scope, while SIZ stock/name samples are retired.

## Additional endpoint checks

Selection update, 2026-10-05: the user clarified that the only available version
is canonical. The release-documentation findings below remain evidence, but
missing documentation no longer excludes a sole available research dataset.
The exact choices are in [CRSP selections](../catalog/canonical-crsp.json) and
[other selections](../catalog/canonical-other.json). These distinguish actual
replacements from denied copies, different samples and internal tables.
Canonical selection does not claim that WRDS still updates the data.

[WRDS Included Data](https://wrds-www.wharton.upenn.edu/pages/about/included-data-on-wrds/)
currently lists Blockholders and SEC Disclosure of Order Execution. Their
recorded endpoint identities and layouts support `block_all`'s three and
`doe_all`'s two tables as offered products. Empty vendor cards are not evidence
of retirement; current offering does not imply recent observation years.

The [current linking matrix](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/)
recommends People Link. Its [official launch](https://wrds-www.wharton.upenn.edu/pages/news/wrds-newsletteroctober-2022/)
names ExecuComp, BoardEx and CIQ; recorded identifiers and February 2025 table
comments corroborate six pair-table endpoints. Link score, cardinality and
row access still require task-specific checks.

`public_all`'s MEPS tables remain unresolved: the [healthcare page](https://wrds-www.wharton.upenn.edu/pages/healthcare-research/)
identifies the subject but not these exact endpoints. The [WRDS vendor listing](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-wrds/)
names `wta_gutenberg`; no observed dependency links it to the visible
`gutenberg.gutenberg_book`, so that endpoint remains unresolved. Unversioned
`pwt_all.na` has 1996-base expenditure columns but no established release
identity; its explicit unresolved override prevents treating it as either
[current PWT](https://www.rug.nl/ggdc/productivity/pwt/) or a known sibling
version solely from schema membership.

## Changes to the skills

- Current CIZ stock/index recipes, current identifier history, and TFZ Treasury
  routes replace executable legacy examples. Current historical periods remain.
- Product references now cover mutual funds, Treasuries, Global Compustat,
  ExecuComp, and all current OptionMetrics families using recorded columns.
- Manual OptionMetrics-CUSIP matching uses `stksecurityinfohist` and its
  `secinfostartdt/secinfoenddt/cusip` fields; effective-time matching is retained.
- BRFitted raw metadata explicitly defines theta per year and vega per
  volatility percentage point. Inherited unverified universal Greek-unit
  statements and the fixed 100-step pricing claim were removed.
- Product tables and documentation dates describe discovery, not complete
  observation coverage; distant date maxima on WRDS product pages can be
  sentinels and are not interpreted as future observations.
