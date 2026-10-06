# TAQ catalog binding and product lifecycle

Use [wrds-catalog](../../wrds-catalog/SKILL.md) for the dated account inventory.
TAQ PostgreSQL metadata is discovery evidence only; this toolkit executes TAQ
through `wrds-taq-agent`, SAS, and `wrds-ssh`. A PostgreSQL annual schema is not
a SAS libref. A successful metadata open does not prove every observation can
be read, nor that every expected trading day is present.

## Live SAS evidence, 2026-10-05

The metadata-only prototype opened `TAQMSEC.CTM_20241007` with `PROC CONTENTS`
under qsas job **40376301**. It completed with `SYSCC=0`, returning 17 variables.
It confirms date and numeric SAS time fields, text root/suffix and trade
condition/correction codes, numeric price/size/sequence fields, and current
participant/TRF timestamp fields. No trade observations were selected.

The library probe confirms four assigned aliases and 16 distinct physical
paths. Repeated `dictionary.libnames` rows were deduplicated; they are not
additional subscriptions or copies of independent datasets.

| SAS alias | Verified path binding | Product routing |
|---|---|---|
| `TAQMSEC` | Ten paths under `/wrds/nyse/sasdata/`: `taqms/{ct,cq,luld_ct,luld_cq,mast,nbbo,nbbod2m}`, plus `wrds_taqms_{nbbo,wct,iid}` | Daily/millisecond family and WRDS derived products |
| `TAQ` | `/wrds/taq/sasdata` plus `wrds_taqs_{ct,nbbo,iid_v1}` under `/wrds/nyse/sasdata` | Historical monthly/second-era TAQ; use for a specifically requested legacy-era analysis |
| `TAQMSAMP` | `/wrds/taqmssamp/sasdata` | Millisecond sample, separately labeled |
| `TAQSAMP` | `/wrds/taqsamp/sasdata` | Historical TAQ sample, separately labeled |

The full metadata job **40376344** completed in 38 minutes 46 seconds with
`SYSCC=0` and no SAS errors or warnings. Its `dictionary.tables` and
`dictionary.columns` queries were restricted to these four aliases. The
validated inventory has **82,212 logical members**, **78 distinct layouts**,
2,521 representative column definitions and 1,154,370 expanded definitions.
Every member has a layout with its exact header variable count; mismatch
count is zero. Library counts are `TAQMSEC` 59,473, `TAQ` 22,719,
`TAQMSAMP` 6 and `TAQSAMP` 14.

The member inventory, member-to-layout map and distinct layout columns are
the source for the SAS catalog. A separate complete-pipeline probe
(job **40376634**) validated three
members, two layouts, and 59 expanded column definitions. Sixteen synthetic
cases verified that every metadata field affects the hash, including labels,
formats and informats beyond character 200, and that the production expression
matches an explicit 256-character buffer. This validates the metadata pipeline;
it does not substitute for a bounded observation extraction.
ISSM and NASTRAQ are separate historical products, retained in PostgreSQL
catalog diagnosis; this SAS inventory does not claim to cover their files.

### Observed Daily TAQ families

These are exact member counts in `TAQMSEC`, including historical partitions.
Bounds come from filenames, not observation dates or calendar validation.
Layouts include differences in types, lengths, labels and formats, so equal
variable counts need not imply the same layout.

| Family | Members | Layouts | Filename bounds | Variables |
|---|---:|---:|---|---:|
| `CTM` | 5,803 | 8 | 20030910–20261002 | 12–17 |
| `CQM` | 5,803 | 10 | 20030910–20261002 | 17–27 |
| `NBBOM` | 5,805 | 12 | 20030910–20261002 | 30–39 |
| `COMPLETE_NBBO` | 5,803 | 9 | 20030910–20261002 | 11 |
| `WCT` | 5,803 | 6 | 20030910–20261002 | 15 |
| `MASTM` | 5,668 | 6 | 20030910–20261002 | 6–40 |
| `NBBOD2M` | 2,952 | 2 | 20150102–20261002 | 13 |
| `LULD_CQM` | 2,199 | 1 | 20180102–20261002 | 12 |
| `LULD_CTM` | 2,199 | 1 | 20180102–20261002 | 11 |
| `WRDS_IID` | 24 | 3 | 2003–2026 | 198 |

The same alias also exposes four-column `IX_CQM`, `IX_CTM` and `IX_NBBOM`
members (5,804, 5,803 and 5,805 respectively), `CHARS`, and the exact unusual
member `MASTM_2011060`. Preserve that seven-digit suffix; do not silently
repair it into a trading date. Inspect auxiliary layouts before choosing a
research source. The catalog groups 38 library/family combinations across
all four aliases, including monthly `DIV`/`MAST` files in legacy TAQ.
`TAQ.WRDS_IID` is an unpartitioned member in addition to its 22 annual
members; do not append both without checking overlap.

## Closed years are not a retired Daily TAQ product

The public [WRDS TAQ product directory](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/nyse-trade-and-quote-taq/)
labels many individual `taqm_YYYY` year cards as no longer updated. Preserve
that source label, but distinguish the completed annual partition from its
parent product. For this snapshot, exact `taqm_2003`–`taqm_2026` schemas
and the `taqmsec` alias belong to the maintained Daily TAQ family. Keep old
years eligible for historical analysis within that family; exclude unrelated
`_old`/`_new` staging or alternate versions from default routing.

This is a stated catalog interpretation supported by NYSE's ongoing
[Daily TAQ product](https://www.nyse.com/data-products/catalog/daily-taq), its
[current and historical technical specifications](https://www.nyse.com/market-data/technical-documents),
and the WRDS [Daily TAQ-to-CRSP linking manual](https://wrds-www.wharton.upenn.edu/documents/1336/NYSE_Daily_TAQ_to_CRSP_Linking_BPNFjWm.pdf),
which distinguishes monthly TAQ (1993–2014) from Daily TAQ (2003 onward).
It does not assert that WRDS continues revising each closed annual partition.

The NYSE technical-documents page retrieved 2026-10-05 lists Daily TAQ v4.3
(June 2026) and historical versions. Select the specification for the file's
era. Do not use the currently published specification to reinterpret an old
field layout without checking its transition history.

## Select and validate a member

1. Choose product and date, then use the SAS member catalog to establish that
   exact `LIBNAME.MEMNAME` and its layout. For modern trades, use
   `TAQMSEC.CTM_YYYYMMDD`; for WRDS NBBO, use
   `TAQMSEC.COMPLETE_NBBO_YYYYMMDD`, not legacy `NBBO_YYYYMMDD`.
2. Inspect the member's actual ordered columns, types, lengths, formats and
   labels. A new era can change its layout despite an unchanged file prefix.
3. Run the one-asset/week prototype and validate observed dates, clocks,
   missing endpoints, counts and keys. Filename minima/maxima in the catalog
   are filename bounds, not validated observation coverage.
4. For concatenated aliases, retain the alias and physical library bindings;
   duplicate physical member names can be shadowed. Do not count aliases or
   duplicate metadata-library rows as independent datasets.

The source repository retains the SAS programs in
`scripts/wrds_taq_inventory/`, metadata artifacts in `catalog/taq/`, and
task-specific logs with account home paths removed. Source `NOBS` values are
SAS header metadata; the inventory does not perform row counts or export
research observations.
