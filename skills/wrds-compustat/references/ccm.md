# Compustat fundamentals and CCM

Migrated 2026-10-05 from the former CRSP agent. Original counts and verification assertions were not accompanied by dated output. The reference below distinguishes those historical notes from operating rules. Load `wrds-schema` for exact table/column checks; subscriptions can differ.

## Fundamentals

| Table | Grain and use | Common fields |
|---|---|---|
| `comp.funda` | Annual company fundamentals | `gvkey`, `datadate`, `fyear`, `at`, `ceq`, `ni` |
| `comp.fundq` | Quarterly company fundamentals | `gvkey`, `datadate`, `fyearq`, `fqtr`, `atq`, `ceqq`, `niq`, `rdq` |
| `comp.company` | Company identification/descriptors | Verify the needed identifiers and fields; current descriptors are not a full historical security map |

`gvkey` is a company identifier, typically six-character zero-padded text on WRDS. It is not a PERMNO or an individual share class. Retain the original string. `datadate` is the fiscal period end; fiscal years do not always coincide with calendar years.

For the standard North American domestic industrial consolidated sample:

```sql
indfmt = 'INDL' AND datafmt = 'STD' AND popsrc = 'D' AND consol = 'C'
```

These filters select a reporting population and prevent common format duplicates. They do not guarantee a unique firm-period key in every query. If the user requests financial services formats, international companies, unconsolidated accounts, or another population, specify the appropriate filters instead of silently excluding the target population. Keep the filter columns in a diagnostic sample.

Common monetary fundamentals are reported in millions of the field's reporting currency; verify item definitions and `curcd`/`curcdq` before combining companies or multiplying by price/share measures. Do not assume all items share the same scale: per-share values, ratios, and shares have their own definitions. CRSP capitalization is commonly in dollars in thousands, so aligning it with a monetary Compustat item requires an explicit unit conversion.

## Availability and revisions

`datadate <= portfolio_date` does not prove accounts were public by formation. Choose one of these designs explicitly:

- Match an observed publication/filing date for the actual information item, allowing processing time if needed.
- Apply a declared reporting-lag convention when publication evidence is unavailable; the sample recipe uses six months for annual accounts.
- For a descriptive contemporaneous merge, label it accordingly and do not claim it represents an investable information set.

Quarterly `rdq` is an earnings announcement date; it is not proof that every accounting item was disclosed that day. Ordinary Compustat files can contain restated data, so publication-date filtering alone does not reconstruct the historical data vintage.

## CCM table choice

Prefer `crsp.ccmxpf_lnkhist` for research links. Its `lpermno` column maps to CRSP's `permno`; the linked column is not named `permno`. A session check preceding migration confirmed `lpermno`.

| Column | Inherited WRDS type | Meaning |
|---|---|---|
| `gvkey` | varchar | Compustat company key |
| `lpermno` | double precision | Linked CRSP security; cast to integer in exports if appropriate |
| `lpermco` | double precision | Linked CRSP company |
| `linkdt` | date | First effective link date |
| `linkenddt` | date | Last effective link date; NULL denotes an open range on WRDS |
| `linktype` | varchar | Link relationship/quality |
| `linkprim` | varchar | Primary/secondary issue marker |
| `liid` | varchar | Linked Compustat issue identifier |

`crsp.ccmxpf_linktable` additionally includes `usedflag`. Do not assume it is interchangeable with the full history table without checking the requested sample. `crsp.ccm_lookup` is a convenience lookup containing company descriptors (`conm`, `tic`, `cusip`, `cik`, `sic`, `naics`, `gsubind`, `gind`, `year1`, `year2` in the former source); it does not expose the same `linktype`/`linkprim` controls. Use the history table for reproducible selection. CCM views may require a subscription beyond CRSP stock access.

## Link flags

The compact definitions below follow the [CRSP/Compustat Merged Database Guide](https://wrds-www.wharton.upenn.edu/documents/402/CRSP-Compustat_Merged_Database_Data_Guide_9efDcmD.pdf), checked 2026-10-05. They correct the old agent's descriptions of LS/LX/LD and J/N.

| `linktype` | Interpretation | Standard sample |
|---|---|---|
| `LC` | Researched standard connection | Include |
| `LU` | CUSIP-based issue link not researched further | Include |
| `LS` | Link applies to this security; other securities of its PERMCO can map elsewhere | Only with explicit design |
| `LX` | Security trades on a foreign exchange outside CRSP's coverage | Exclude |
| `LD` | Duplicate relationship; another GVKEY/IID is preferred | Exclude |
| `LN` | Primary relationship, but Compustat price information unavailable | Outside default sample |
| `NR`, `NU`, `NP` | No usable standard link / legacy no-link classifications | Exclude; verify detailed historical code if needed |

| `linkprim` | Interpretation |
|---|---|
| `P` | Primary issue designated by Compustat |
| `C` | Primary issue designated by CRSP to resolve Compustat history |
| `J` | Compustat secondary/joiner issue |
| `N` | CRSP secondary designation |

The standard primary-security sample uses `linktype IN ('LC','LU')` and `linkprim IN ('P','C')`, together with a valid linked security and date range. A prefix filter such as `SUBSTR(linktype,1,1)='L'` also admits duplicate, foreign, and other nonstandard relationships; it is not a substitute for a deliberate quality filter.

## Dates and cardinality

Match the chosen observation date inclusively between `linkdt` and `COALESCE(linkenddt, DATE '9999-12-31')`. Use the raw CRSP trading date for a security-month link. A fiscal-date, formation-date, or company-history mapping may instead need a different anchor; record which one the research design uses. Investigate NULL starts if present rather than silently treating them as a universal open start.

The P/C flags aim to identify a primary security, but validate cardinality on the actual sample and in the relevant direction. One security mapping to several GVKEYs is not ruled out merely by a claim about one GVKEY's primary security. A company with several PERMNOs over history may have sequential restructurings or multiple classes; inspect the effective intervals.

Use CCM rather than a bare CUSIP match for CRSP-Compustat production merges. CUSIP values and issuer/security identities change with corporate actions, and a current CUSIP is not a complete historical link.

An accounting lookback of 18 months can admit more than one annual observation. Apply availability rules first, check source uniqueness and link multiplicity, then select the latest eligible `datadate`. `ROW_NUMBER()` solves the choice among reporting periods; it should not silently settle contradictory source rows or links.

## Historical source snapshot

The retired source recorded 123,388 rows in `ccmxpf_lnkhist`, 92,711 in `ccmxpf_linktable`, and 6,383 NULL link-end dates. It listed LC 17,932; LU 15,945; LS 7,159; LX 1,176; LD 119; and 81,057 combined no-link/other rows. It listed P 54,596; C 58,201; J 3,896; N 6,695.

It also claimed no overlapping primary links and equality between selected `linktable` and `lnkhist` rows. The source retained neither the verification date nor the checking query. These are historical diagnostics, not current guarantees; do not reuse them as validation evidence.
