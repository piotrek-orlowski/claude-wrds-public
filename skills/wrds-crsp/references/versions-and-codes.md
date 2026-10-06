# Current CRSP CIZ codes

Use exact-table metadata for uncertain definitions. `crsp.metaiteminfo` and
`crsp.metaflaginfo` provide item and flag descriptions; `metasiztociz` is a
conversion aid, not an alternative stock product.

## Excluded product and replacement

SIZ/v1 Stock and Indexes is retired: WRDS identifies December 2024, released
in February 2025, as its final release. This toolkit uses CIZ/v2, including its
historical observations. It does not query old `dsf`/`msf`/name/event recipes
or fill a current-product access failure with the frozen files.
[WRDS transition notice](https://wrds-www.wharton.upenn.edu/pages/data-announcements/changes-to-crsp-data/)

The current files use `dlycaldt`/`mthcaldt`, `dlyret`/`mthret`, positive prices
plus source flags, and explicit classification fields. Monthly returns compound
daily returns with dividends reinvested on ex-dates; delisting returns are
already incorporated. Do not mix calculation conventions across versions.

## Classification codes

The following compact code reference was inherited from the repository's
prior CRSP material; confirm codes against the selected CIZ metadata.

| Field | Recorded values |
|---|---|
| `primaryexch` | N=NYSE, A=AMEX, Q=NASDAQ, R=Arca, B=BZX |
| `securitytype` | EQTY, FUND, DERV |
| `securitysubtype` | COM=common, ETF, CEF=closed-end fund |
| `sharetype` | NS=normal, CE=certificate, AD=ADR, SB=SBI, UG=unit |
| `issuertype` | ACOR=actively traded corporation, CORP=corporation, REIT |
| `usincflg` | Y/N |

| Example population | CIZ selection |
|---|---|
| US common stocks | `sharetype='NS' AND securitytype='EQTY' AND securitysubtype='COM' AND usincflg='Y'` |
| Major exchanges | `primaryexch IN ('N','A','Q')` |
| ETFs | `securitysubtype='ETF'` |
| Nonmissing daily returns | `dlyret IS NOT NULL AND dlyretmissflg IS NULL` |

These are research sample choices. Add issuer, trading-status, and conditional
flags only when the requested universe calls for them. Keep a valid total-loss
return of -1; investigate any value below -1 rather than treating it as a return.

## Return missing flags (`dlyretmissflg`)

| Code | Meaning |
|---|---|
| `NS` | New security / first period |
| `RA` | Return after a not-tracked period |
| `GP` | Gap between prices too large |
| `MP` | Missing price |
| `NT` | Not tracked |
| `DG` | Delisting gap |
| `DM` | Delisting, missing |
| `DP` | Delisting, partial |
| `MV` | Moved |
| NULL | No missing-return flag |

Also inspect return duration and other relevant flags. The absence of this
flag does not establish that every expected trading day exists.

## Price flags (`dlyprcflg`)

| Code | Meaning |
|---|---|
| `TR` | Closing trade |
| `BA` | Bid-ask average |
| `MP` | Missing price |
| `NT` | Not tracked |
| `SU` | Suspended |

A bid-ask-average price is a separate price source, not automatically an invalid
observation. See [returns and adjustments](returns-and-adjustments.md) for
compounding and [schema](schema.md) for current security-history and event fields.
