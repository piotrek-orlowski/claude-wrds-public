# TAQ SAS products and schema

Migrated from the repository TAQ expert's **2026-02-27** notes. The newer **2026-10-05** [SAS catalog](catalog.md) supplies current member names, layouts and library bindings, including master files before 2009. The remaining field descriptions below are inherited guidance. Use the exact member layout and a small SAS probe for the requested era before extraction; metadata does not establish observation coverage.

## WRDS TAQ Directory Layout (verified 2026-02-27)

The recorded layout includes `/wrds/nyse/sasdata/` and the legacy directories below. Do not substitute one legacy directory for another: their observed coverage differs.

```
/wrds/nyse/sasdata/
    taqms/                      # TAQ Millisecond raw data (2003-present)
        ct/                     # Trades: ctm_YYYYMMDD.sas7bdat
        cq/                     # Quotes: cqm_YYYYMMDD.sas7bdat
        nbbo/                   # NBBO: nbbom_YYYYMMDD.sas7bdat + ix_nbbom_YYYYMMDD
        mast/                   # Master: mastm_YYYYMMDD.sas7bdat (catalog filenames start 2003-09-10; layouts vary)
        nbbod2m/                # NBBO daily-to-monthly: nbbod2m_YYYYMMDD (starts 2015-01-02)
        luld_ct/                # LULD trade halts: luld_ctm_YYYYMMDD (starts 2018-01-02)
        luld_cq/                # LULD quote halts: luld_cqm_YYYYMMDD (starts 2018-01-02)
    taqs/                       # Legacy monthly (1993-2014, but ends 2014-07-31 — incomplete)
    wrds_taqms_nbbo/            # WRDS-computed NBBO: complete_nbbo_YYYYMMDD (2003-present)
    wrds_taqms_wct/             # WRDS Consolidated Trades: wct_YYYYMMDD (2003-present)
    wrds_taqms_iid/             # WRDS Intraday Indicators: wrds_iid_YYYY (2003-present, annual)
    wrds_taqs_ct/               # WRDS Consolidated Trades, legacy: wct_YYYYMMDD (1993-2014)
    wrds_taqs_nbbo/             # WRDS-computed NBBO, legacy: nbbo_YYYYMMDD (1993-2014)
    wrds_taqs_iid_v1/           # WRDS Intraday Indicators v1, legacy: wrds_iid_YYYY (1993-2014)

/wrds/taq/sasdata/              # Legacy monthly (1993-01-04 through 2014-12-31) — COMPLETE range
                                # Contains ct_YYYYMMDD, cq_YYYYMMDD
```

## SAS Library Aliases (verified via dictionary.libnames)

### `taqmsec` — Millisecond era (CONCATENATED, 10 paths)

This is the primary library for all millisecond-era TAQ data. It concatenates:

```
1.  /wrds/nyse/sasdata/taqms/ct          → ctm_YYYYMMDD, luld_ctm_YYYYMMDD
2.  /wrds/nyse/sasdata/taqms/cq          → cqm_YYYYMMDD, luld_cqm_YYYYMMDD
3.  /wrds/nyse/sasdata/taqms/luld_cq     → luld_cqm_ (duplicates of #2)
4.  /wrds/nyse/sasdata/taqms/luld_ct     → luld_ctm_ (duplicates of #1)
5.  /wrds/nyse/sasdata/taqms/mast        → mastm_YYYYMMDD
6.  /wrds/nyse/sasdata/taqms/nbbo        → nbbom_YYYYMMDD, ix_nbbom_YYYYMMDD
7.  /wrds/nyse/sasdata/taqms/nbbod2m     → nbbod2m_YYYYMMDD
8.  /wrds/nyse/sasdata/wrds_taqms_nbbo   → complete_nbbo_YYYYMMDD
9.  /wrds/nyse/sasdata/wrds_taqms_wct    → wct_YYYYMMDD
10. /wrds/nyse/sasdata/wrds_taqms_iid    → wrds_iid_YYYY
```

**Usage:** `taqmsec.ctm_20250115`, `taqmsec.cqm_20250115`, `taqmsec.nbbom_20250115`,
`taqmsec.complete_nbbo_20250115`, `taqmsec.wct_20250115`, `taqmsec.mastm_20250115`

### `taq` — Legacy era (CONCATENATED, 4 paths)

```
1. /wrds/taq/sasdata                     → ct_YYYYMMDD, cq_YYYYMMDD (1993-2014)
2. /wrds/nyse/sasdata/wrds_taqs_ct       → wct_YYYYMMDD (1993-2014)
3. /wrds/nyse/sasdata/wrds_taqs_nbbo     → nbbo_YYYYMMDD (1993-2014)
4. /wrds/nyse/sasdata/wrds_taqs_iid_v1   → wrds_iid_YYYY (1993-2014)
```

**Usage:** `taq.ct_20100115`, `taq.cq_20100115`, `taq.nbbo_20100115`, `taq.wct_20100115`

### Other libraries

- **`taqsamp`** — TAQ samples (`/wrds/taqsamp/sasdata`)
- **`taqmsamp`** — TAQ millisecond samples (`/wrds/taqmssamp/sasdata`)
- **`wrdsapps`** — TAQ-CRSP linking (`wrdsapps.taqmclink`) and event study tools

### Libraries that do NOT exist

`taqms`, `taqm`, `taqs`, `taqmast`, `taqnbbo`, `taqwct`, `nbbo`, `wct`, `luld`, `taqluld`, `taqiid`, `wrds` did not resolve in the recorded session. Use `taqmsec` or `taq` for the main products; confirm aliases with `dictionary.libnames` when needed.

## Core Expertise

### TAQ Data Products

| Product | SAS Library | File Pattern | Date Range |
|---------|-------------|--------------|------------|
| Trades (ms) | `taqmsec` | `ctm_YYYYMMDD` | 2003-09-10 – present |
| Quotes (ms) | `taqmsec` | `cqm_YYYYMMDD` | 2003-09-10 – present |
| NBBO (ms) | `taqmsec` | `nbbom_YYYYMMDD` | 2003-09-10 – present |
| Master | `taqmsec` | `mastm_YYYYMMDD` | **2003-09-10 – 2026-10-02 filename bounds** in the 2026-10-05 catalog; observation coverage unverified |
| NBBO daily-to-monthly | `taqmsec` | `nbbod2m_YYYYMMDD` | 2015-01-02 – present |
| LULD trades | `taqmsec` | `luld_ctm_YYYYMMDD` | 2018-01-02 – present |
| LULD quotes | `taqmsec` | `luld_cqm_YYYYMMDD` | 2018-01-02 – present |
| WRDS NBBO | `taqmsec` | `complete_nbbo_YYYYMMDD` | 2003-09-10 – present |
| WRDS Consolidated Trades | `taqmsec` | `wct_YYYYMMDD` | 2003-09-10 – present |
| WRDS Intraday Indicators | `taqmsec` | `wrds_iid_YYYY` | 2003 – present |
| Legacy trades | `taq` | `ct_YYYYMMDD` | 1993-01-04 – 2014-12-31 |
| Legacy quotes | `taq` | `cq_YYYYMMDD` | 1993-01-04 – 2014-12-31 |
| Legacy WRDS NBBO | `taq` | `nbbo_YYYYMMDD` | 1993-01-04 – 2014-12-31 |
| Legacy WRDS Consol. Trades | `taq` | `wct_YYYYMMDD` | 1993-01-04 – 2014-12-31 |

**CRITICAL — WRDS NBBO naming:**
- Millisecond era: **`complete_nbbo_YYYYMMDD`** (NOT `nbbo_YYYYMMDD`)
- Legacy era: `nbbo_YYYYMMDD`

### Timestamp Evolution (recorded era guide)

| Period | Precision | Format |
|--------|-----------|--------|
| 1993 – Oct 2003 | Seconds | `HHMMSS` |
| Oct 2003 – Jul 2015 | Milliseconds | `HHMMSSxxx` |
| Jul/Aug 2015 – Oct 2016 | Microseconds | `HHMMSSxxxxxx` |
| Oct 2016 – present | Nanoseconds | `HHMMSSxxxxxxxxx` |

Confirm the requested file's type and format with `PROC CONTENTS`; these era boundaries are approximate inherited notes. SAS numeric time is not an HHMMSS integer. Displayed precision does not establish clock accuracy, and numeric storage can limit preserved subsecond precision.

### Key Variables — Trades (ctm_ millisecond)

- `TIME_M`: Transaction timestamp
- `SYM_ROOT`/`SYM_SUFFIX`: Security identifier
- `PRICE`: Trade price
- `SIZE`: Trade volume (shares)
- `EX`: Exchange code
- `TR_CORR`: Trade correction indicator (text: '00'=regular, '01'=corrected, '07'/'08'=error/cancel)
- `TR_SCOND`: Sale condition codes (up to 4 characters)
- `TR_SOURCE`: Source of trade ('C'=CTA, 'N'=UTP)
- `PART_TIME`: Participant timestamp
- `TR_SEQNUM`: Trade sequence number

### Key Variables — Trades (ct_ legacy, pre-2015)

- `TIME`: Transaction timestamp (seconds)
- `SYMBOL`: Security identifier (10 chars)
- `PRICE`: Trade price
- `SIZE`: Trade volume
- `EX`: Exchange code
- `CORR`: Correction indicator (numeric)
- `COND`: Sale condition (2 characters)

### Key Variables — Quotes (cqm_)

- `TIME_M`: Quote timestamp (millisecond data)
- `SYM_ROOT`/`SYM_SUFFIX`: Security identifier
- `BID`, `ASK`: Bid and ask prices
- `BIDSIZ`, `ASKSIZ`: Bid and ask sizes (round lots)
- `EX`: Exchange code
- `QU_COND`: Quote condition
- `NATBBO_IND`: National BBO indicator
- `QU_CANCEL`: Quote cancel/correction indicator
- `SSR`: Short Sale Restriction indicator

### Key Variables — NBBO (nbbom_)

- `TIME_M`: Quote timestamp
- `SYM_ROOT`/`SYM_SUFFIX`: Security identifier
- `BEST_BID`, `BEST_BIDEX`, `BEST_BIDSIZ`: Best bid price, exchange, size
- `BEST_ASK`, `BEST_ASKEX`, `BEST_ASKSIZ`: Best ask price, exchange, size
- `BID`, `ASK`, `BIDSIZ`, `ASKSIZ`: Quote that triggered the NBBO update
- `NATBBO_IND`: Effect of quote on NBBO
- `NBBO_QU_COND`: Status of NBBO (open/closed)

### Key Variables — Master (mastm_; layout varies by era)

- `SYM_ROOT`, `SYMBOL_15`: Security identifiers
- `CUSIP`: 9-digit CUSIP
- `TAPE`: Tape A, B, or C
- `UOT`: Unit of trade (lot size)
- `ROUND_LOT`: Round lot size
- `SEC_TYPE`: Security type
- `LISTED_EXCHANGE`: Listing exchange

The catalog includes `TAQMSEC.MASTM_20030910` with six variables and records six master layouts with 6–40 variables overall. Do not assume every member contains all fields listed above. The successful header opens and filename bounds establish member existence and schema, not complete dates or readable observation coverage.

**IMPORTANT:** In TAQ millisecond data (taqmsec):
- Symbol variable is `SYM_ROOT` (not `SYMBOL_ROOT`)
- Timestamp variable is `TIME_M` (not `TIME`)
- Ask price is `ASK` (not `OFR`)
- Ask size is `ASKSIZ` (not `OFRSIZ`)
Always verify variable names with `PROC CONTENTS` before writing extraction code.

### Trading Hours Coverage

Typical windows in the inherited notes are below. Confirm the exchange calendar, early closes, timezone, and the requested product's actual coverage before choosing a window:
- Pre-market: 4:00 AM – 9:30 AM ET
- Regular market: 9:30 AM – 4:00 PM ET
- After-hours: 4:00 PM – 8:00 PM ET

Sale-condition examples from the inherited notes (confirm feed and date-specific definitions, including combinations of flags):
- `'T'` = Extended Hours Trade (Sold Out of Sequence)
- `'U'` = Extended Hours Trade (Reported Late or Out of Sequence)
- Regular hours typically use conditions: `' '`, `'@'`, `'E'`, `'F'`, `'I'`, `'J'`

### WRDS-Created Datasets (use these to save processing time)

- **`complete_nbbo_YYYYMMDD`**: WRDS-computed National Best Bid and Offer (millisecond era). Access via `taqmsec.complete_nbbo_YYYYMMDD`. Physical path: `/wrds/nyse/sasdata/wrds_taqms_nbbo/`
- **`nbbo_YYYYMMDD`**: WRDS-computed NBBO (legacy era only). Access via `taq.nbbo_YYYYMMDD`. Physical path: `/wrds/nyse/sasdata/wrds_taqs_nbbo/`
- **`wct_YYYYMMDD`**: WRDS Consolidated Trades with matched NBBO midpoints at t, t-1, t-2, t-5 seconds. Access via `taqmsec.wct_YYYYMMDD` or `taq.wct_YYYYMMDD`
- **`wrds_iid_YYYY`**: WRDS Intraday Indicators (annual files). Access via `taqmsec.wrds_iid_YYYY`
- **`nbbod2m_YYYYMMDD`**: NBBO daily-to-monthly (2015+). Access via `taqmsec.nbbod2m_YYYYMMDD`

### Exchange Codes (Recorded Examples)

- `N` = NYSE
- `T`/`Q` = NASDAQ
- `P` = NYSE Arca
- `Z` = BATS
- `K` = CBOE EDGX
- `V` = IEX
