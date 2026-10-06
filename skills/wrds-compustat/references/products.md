# Current Compustat products

Checked 2026-10-05 using the public
[WRDS S&P product listing](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sp-global-market-intelligence/)
and live metadata. Load [wrds-catalog](../../wrds-catalog/SKILL.md) for complete
tables, columns, alias dependencies, and access evidence. Planning success is
not a row-read guarantee. All access statements here describe one account on
the check date.

## Choose the product

| Product | Underlying schema | Discovery result |
|---|---|---|
| North America current and historical | `comp_na_daily_all` | Schema usage; 206 tables |
| Global | `comp_global_daily` | Schema usage; 125 tables |
| ExecuComp | `comp_execucomp` | Schema usage; 15 tables; alias `execcomp` |
| Bank | `comp_bank_daily` | Separate current product; schema usage denied |
| Historical segments | `comp_segments_hist_daily` | Separate current product; schema usage denied |
| Snapshot | `comp_snapshot` | Separate current product; schema usage denied |
| Point in time | `comp_pit` | Separate current product; schema usage denied |
| Preliminary history | `comp_ph` | Separate current product; schema usage denied |

The WRDS page reports 2026 refreshes for these products. `snapshot`, `hist`,
and old observation dates are not evidence of a retired version. Ordinary
Compustat history can contain revisions; neither a fiscal-date filter nor a
reporting lag reconstructs a historical database vintage. Use a licensed
point-in-time/snapshot product when the design requires that distinction.

`comp` contains mixed-product aliases. An alias grant does not establish
access to its underlying product. Preserve the resolved source schema in the
extract manifest. Alternate `_old` delivery schemas are outside current
recipes; their exact retention policy is unresolved, not inferred from the
suffix. The Global `g_tmptable_pkg6775_tbl5551` placeholder has unresolved
purpose and is not promoted to a research table.

## North America

Use `comp.funda`/`fundq` for the standard annual/quarterly accounting panels,
with [accounting and CCM rules](ccm.md) and [bounded recipes](queries.md).
Keep the format dimensions until their sample restrictions are explicit.

Other modules are discoverable in the same current product:

| Module | Tables |
|---|---|
| Company/security identity | `company`, `security`; `gvkey` vs `gvkey,iid` grain |
| Security prices | `secd`, `secm` |
| Industry history | `co_hgic` |
| Exchange rates | `exrt_dly`, `exrt_mth` |
| Indexes/constituents | `idx_daily`, `idx_mth`, `idx_index`, `idxcst_his`, `indexcst_his` |
| Segments | `names_seg`, `seg_ann`, `seg_annfund`, `seg_customer`, `seg_geo`, `seg_naics`, `seg_product`, `seg_type`, `wrds_segmerged` |
| Footnotes/dictionaries | `funda_fncd`, `fundq_fncd`, `dd_item`, `dd_group`, `dd_group_xref`, `dd_package`, `xfl_table`, `xfl_column` |

A security price panel may have several issues per company. An index or
segment panel has additional identities, dates, and classification dimensions;
do not collapse it to one `gvkey,datadate` row. Segment totals may overlap or
include eliminations. Inspect segment type and reporting basis before summing.

## Global

Use `comp.g_funda`/`g_fundq` for consolidated panels where appropriate.
The verified `g_funda` fields include `gvkey,datadate,indfmt,datafmt,consol,
popsrc,curcd,acctstd,pddur,fyear,fyr,pdate,fdate,at,sale`, and security/header
identifiers. A domestic North America filter such as `popsrc='D'` must not be
copied blindly: inspect Global population/format values on the pilot.

| Module | Tables |
|---|---|
| Identity/history | `g_company`, `g_security`, `g_sec_history`, `g_secnamesd`, `gsecnamesm`, `g_sedolgvkey` |
| Price and return inputs | `g_secd`, `g_secm`, `g_sec_dprc`, `g_sec_dtrt`, `g_sec_adjfact`, `g_sec_divid`, `g_sec_split` |
| Interim reporting | `g_co_ifndq`, `g_co_ifndsa`, `g_co_ifndytd` |
| Indexes/constituents | `g_idx_daily`, `g_idx_mth`, `g_idx_index`, `g_idxcst_his`, `g_indexcst_his` |
| Currency/industry | `g_currency`, `g_exrt_dly`, `g_exrt_mth`, `wrds_g_exrate`, `g_co_hgic` |
| Detail/footnotes | `g_co_*` financial-item modules; `g_funda_fncd`, `g_fundq_fncd` |

Retain currency, accounting standard, and period duration. Quarterly,
semiannual, and year-to-date flows are different measurements. Do not combine
them without an explicit conversion and coverage test. `fic` and `loc` are
current header incorporation/headquarters fields, not automatically historical
listing country. Company accounts and security prices require separate
currency/issue choices. Preserve preliminary/final dates, but establish what
they mean before treating them as investor information timestamps.

## ExecuComp

Use `execcomp.anncomp` or `comp_execucomp.anncomp` for executive-company-year
work. Verified identifiers include `gvkey,execid,year,co_per_rol`; annual role
fields include `ceoann,cfoann,titleann`, and `old_datafmt_flag` marks format
context. Retain multiple executives per company and role changes within a
year. Do not resolve ambiguity by selecting an arbitrary first executive.

| Need | Tables |
|---|---|
| Aggregate compensation | `anncomp` |
| Company/person/role | `colev`, `person`, `coperol`, `ex_header`, `exnames` |
| Equity awards | `planbasedawards`, `outstandingawards`, `ex_black` |
| Retirement/deferred/directors | `pension`, `deferredcomp`, `directorcomp` |
| Historical layouts retained in current product | `codirfin` (2005 and earlier), `ltawdtab`, `stgrttab` (1992-format tables) |

Historical layouts remain useful for historical observations, even though they
are not the source for current-year awards. Definitions changed around the
2006 reporting transition: `tdc1`, `tdc2`, award fair values, realized option
values, and current compensation are not interchangeable. Verify item units
and definitions before merging periods or calculating pay ratios. See the
[WRDS ExecuComp introduction](https://wrds-www.wharton.upenn.edu/pages/classroom/introduction-execucomp/).

Prototype one company and two fiscal years. Check `gvkey,execid,year` and
`co_per_rol,year` uniqueness, format flags, missing compensation components,
multiple CEOs, and changing role dates. Use dated CCM links only when entitled;
there is no guaranteed CCM access merely because Compustat and CRSP stocks
are both accessible.
