# TAQ–CRSP identifiers and links

This reference preserves linking knowledge from the retired query orchestrator.
Its coverage labels and score descriptions are historical source notes, not
live subscription or endpoint guarantees. Confirm the link relation's schema,
coverage, and documented match codes before production use.

TAQ extraction runs through `wrds-taq-agent` using SAS on WRDS, with
[wrds-taq](../../wrds-taq/SKILL.md) for data knowledge and
[wrds-ssh](../../wrds-ssh/SKILL.md) for submission, monitoring, logs, and transfers.
Direct PostgreSQL companion queries, including a WRDS application link table,
go through `wrds-psql-agent`. SSH is not a PostgreSQL fallback.

## Daily TAQ link table

The source records `wrdsapps.taqmclink` with `sym_root`, `sym_suffix`, `permno`,
`cusip`, `ncusip`, `date`, and `match_lvl`, and coverage starting September 2003.
It describes lower match levels as stronger: 0 CUSIP/name, 1 CUSIP, 2
ticker/name, 3 ticker. Verify these definitions against the current WRDS
documentation rather than interpreting any unrecognized level by analogy.

```sql
SELECT sym_root, sym_suffix, permno, cusip, ncusip, date, match_lvl
FROM wrdsapps.taqmclink
WHERE date = DATE '2020-01-15'
  AND sym_root = 'JNJ'
ORDER BY sym_root, sym_suffix, permno;
```

For a companion sample matched to CRSP returns, follow the
[CRSP skill](../../wrds-crsp/SKILL.md)'s CIZ/v2 default:

```sql
SELECT t.sym_root, t.sym_suffix, t.date, t.permno, t.match_lvl,
       c.dlyret, c.dlyretmissflg
FROM wrdsapps.taqmclink t
JOIN crsp.dsf_v2 c ON t.permno = c.permno AND t.date = c.dlycaldt
WHERE t.date = DATE '2020-01-15'
  AND t.sym_root = 'JNJ'
  AND t.match_lvl <= 1;
```

The score cutoff is the inherited example policy. Keep the code in output and
measure unmatched and rejected rows before using the inner-join result. Match
the trade/quote date and both root and suffix. Daily TAQ source fields may be
named `symbol_root`/`symbol_suffix`, while the application link uses
`sym_root`/`sym_suffix`; confirm and map them explicitly. Normalize NULL/blank
suffixes consistently only after inspecting source semantics. Do not discard a
nonblank suffix because the root resembles an ordinary ticker.

## Monthly TAQ legacy link macro

The source records this SAS macro for Monthly TAQ (historically 1993–2014):

```sas
/* One-month prototype; confirm macro path and interface in the WRDS environment. */
%include "/wrds/lib/sas/tclink.sas";
%tclink(BEGDATE=200301, ENDDATE=200301, OUTSET=WORK.TCLINK);
/* Source-described output: DATE, SYMBOL, PERMNO, CUSIP, SCORE. */
```

The inherited score range is 0 (best) to 3 (weakest). Inspect the actual output
and documentation before imposing a cutoff. Run the macro as part of the TAQ
SAS job, prototype one month, and retain date and symbol when exporting a link.
Do not assume a monthly file implies a symbol is constant throughout that
month or that a CUSIP match is unique.

## Legacy CUSIP formats

| Source | Recorded identifier convention |
|---|---|
| Monthly TAQ | `SYMBOL`; 12-character CUSIP in the master data |
| Daily TAQ | Symbol root plus suffix; nine-character CUSIP and `symbol_15` in the source description |
| CRSP name history | Eight-character historical `ncusip` plus validity dates |

For the Monthly TAQ 12-character format, the first nine characters are the
standard CUSIP and the final three an exchange extension. The old reference
lists extensions `000` NYSE, `001` AMEX, and `002` NASD; treat those as legacy
codes to confirm for the particular master file.

```sas
/* Apply to the CUSIP variable from the chosen TAQ master dataset. */
length cusip9 $9 cusip8 $8 exchange_extension $3;
cusip9 = substr(cusip, 1, 9);
cusip8 = substr(cusip, 1, 8);
exchange_extension = substr(cusip, 10, 3);
```

Keep the original CUSIP, date, symbol, and exchange code. Use the first eight
characters only when comparing with CRSP NCUSIP, together with overlapping
validity dates. For general interval/cardinality checks, return to
[wrds-linking](../SKILL.md).
