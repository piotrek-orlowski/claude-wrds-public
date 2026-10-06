# TAQ SAS implementation examples

Use only the sections needed for the request. These are adaptable source
patterns, not evidence of a completed SAS run. They were reviewed during the
migration but not executed on WRDS. Submit a small prototype using `wrds-ssh`
before scaling. Keep SAS notes and warnings enabled.

## Probe one daily file

```sas
proc contents data=taqmsec.ctm_20241007; run;
proc contents data=taqmsec.nbbom_20241007; run;
proc sql;
    select libname, engine, path
    from dictionary.libnames
    where libname in ('TAQ','TAQMSEC');
quit;
```

Confirm variable names, types, time formats, symbol suffixes, and sequence
fields. Use the library and date appropriate to the requested era.

## Filtered views

The examples select one asset and a regular full trading day. Substitute the
validated date, suffix, conditions, and actual close. The strict sale-condition
allowlist is an explicit example, not a universal TAQ filter.

```sas
%let day = 20241007;
%let ticker = AAPL;
%let suffix = ;
%let session_open = '09:30:00't;
%let session_close = '16:00:00't;

data trades_view / view=trades_view;
    set taqmsec.ctm_&day.
        (keep=time_m sym_root sym_suffix price size tr_corr tr_scond tr_seqnum
         where=(sym_root="&ticker." and sym_suffix="&suffix."
            and tr_corr in ('00','01')
            and tr_scond in (' ','@','E','F')
            and price > 0 and size > 0
            and time_m >= &session_open. and time_m <= &session_close.))
        open=defer;
    date = input("&day.", yymmdd8.);
    log_price = log(price);
    format date yymmdd10.;
run;

data nbbo_view / view=nbbo_view;
    set taqmsec.nbbom_&day. open=defer;
    where sym_root="&ticker." and sym_suffix="&suffix."
        and best_bid > 0 and best_ask > best_bid
        and time_m >= &session_open. and time_m <= &session_close.;
    midquote = (best_bid + best_ask) / 2;
run;

data quotes_view / view=quotes_view;
    set taqmsec.cqm_&day. open=defer;
    where sym_root="&ticker." and sym_suffix="&suffix."
        and qu_cond in ('A','B','H','O','R','W',' ')
        and bid > 0 and ask > bid
        and time_m >= &session_open. and time_m <= &session_close.;
run;
```

The quote examples show price and condition filtering only. Add the selected
product's status and cancellation policy before production sampling. The
`quotes_view` contains exchange quotes; it is not a reconstructed national BBO.
For all-tick trade analysis, `trades_view` already provides positive-price
`log_price` observations before imposing a sampling grid.

## Previous-tick trade sampling on a five-minute grid

This example uses `trades_view` above. Ties within a timestamp are ordered by
`TR_SEQNUM`; validate its scope and uniqueness. A quote-based adaptation needs
its own status/reset policy and sequence key. The five-minute maximum age below
is a research parameter, not a provider rule.

```sas
%let max_age_seconds = 300;

data tick_events;
    set trades_view;
    event_time = time_m;
    event_order = 0;
    source_order = tr_seqnum;
    keep date sym_root sym_suffix event_time event_order source_order price;
run;

data grid_events;
    length sym_root $32 sym_suffix $8;
    date = input("&day.", yymmdd8.);
    sym_root = "&ticker.";
    sym_suffix = "&suffix.";
    event_order = 1;
    source_order = 0;
    do event_time = &session_open. to &session_close. by 300;
        output;
    end;
run;

data events;
    length sym_root $32 sym_suffix $8;
    set tick_events grid_events;
run;
proc sort data=events;
    by date sym_root sym_suffix event_time event_order source_order;
run;

data sampled;
    set events;
    by date sym_root sym_suffix event_time event_order source_order;
    retain last_price last_time;
    if first.sym_suffix then call missing(last_price, last_time);
    if event_order = 0 then do;
        last_price = price;
        last_time = event_time;
    end;
    else do;
        sample_price = .;
        age_seconds = event_time - last_time;
        if not missing(last_time) and age_seconds <= &max_age_seconds.
            then sample_price = last_price;
        output;
    end;
    keep date sym_root sym_suffix event_time sample_price age_seconds;
run;

data sampled_returns;
    set sampled;
    by date sym_root sym_suffix;
    retain previous_price;
    if first.sym_suffix then call missing(previous_price);
    log_return = .;
    if sample_price > 0 and previous_price > 0
        then log_return = log(sample_price / previous_price);
    previous_price = sample_price;
run;

proc sql;
    create table rv_observed as
    select date, sym_root, sym_suffix,
           sum(log_return**2) as observed_rv_5min,
           count(log_return) as n_returns,
           count(*) as n_grid,
           sum(missing(sample_price)) as n_missing_prices
    from sampled_returns
    group by date, sym_root, sym_suffix;
quit;

data rv;
    set rv_observed;
    session_seconds = &session_close. - &session_open.;
    expected_n_returns = floor(session_seconds / 300);
    expected_n_grid = expected_n_returns + 1;
    grid_covers_session = (session_seconds > 0 and mod(session_seconds, 300) = 0);
    complete_grid = (grid_covers_session and n_grid = expected_n_grid
                     and n_returns = expected_n_returns and n_missing_prices = 0);
    rv_5min = .;
    if complete_grid then rv_5min = observed_rv_5min;
run;
```

Trades at a grid timestamp enter before the grid sample. Opening values remain
missing until a valid trade exists; stale endpoints remain missing. A missing
endpoint breaks both adjacent returns instead of creating a return across a
longer gap. `observed_rv_5min` sums only the available interval returns; it can
describe a partial session and is missing if no returns exist. `rv_5min` is
missing unless `complete_grid=1`: every expected endpoint and interval return
must be present. In particular, a missing 09:30 price makes the full-grid measure
missing even if all later intervals are usable.

Expected counts derive from the selected session: 79 grid points and 78 returns
for 09:30–16:00, or 43 and 42 for 09:30–13:00. Require a positive session duration
divisible by 300 seconds so the grid includes the close; otherwise this example
marks the session incomplete. Set the actual session close for each trading day
before running the sampler, and keep the completeness flag beside both measures.

## Event-time and bin sampling alternatives

For the last trade inside each half-open five-minute bin, compute
`interval_num = floor((time_m - &session_open.)/300)`, exclude the exact closing
timestamp or assign it explicitly to the final bin, sort by full security key,
date, bin, time, and sequence, then keep `last.interval_num`. This is not the
same output as the fixed-grid sampler above.

For every Nth eligible quote, first materialize and sort the filtered quote
stream by date, full security key, timestamp, and the verified sequence field.
The following step assumes that ordered input is named `ordered_nbbo` and
contains the normalized `date`, identifiers, and `midquote` columns:

```sas
%let update_interval = 100;
data event_sampled;
    set ordered_nbbo;
    by date sym_root sym_suffix;
    retain counter previous_sample;
    if first.sym_suffix then do;
        counter = 0;
        call missing(previous_sample);
    end;
    counter + 1;
    if mod(counter, &update_interval.) = 0 then do;
        log_return = .;
        if midquote > 0 and previous_sample > 0
            then log_return = log(midquote / previous_sample);
        previous_sample = midquote;
        output;
    end;
run;
```

This is event-time sampling of one asset. Multivariate refresh-time sampling
requires the synchronization rule described in `filters-and-methods.md`.

## Daily-file loop

Use numeric SAS dates for iteration, with `YYYYMMDD` used only for names. This
prototype creates narrow per-day views; replace the inner block with the
validated daily calculation when scaling.

```sas
%macro process_dates(start_date, end_date);
    %local current_day day_name;
    %do current_day = &start_date. %to &end_date.;
        %let day_name = %sysfunc(putn(&current_day., yymmddn8.));
        %if %sysfunc(exist(taqmsec.ctm_&day_name.)) %then %do;
            data day_&day_name. / view=day_&day_name.;
                set taqmsec.ctm_&day_name. open=defer;
                where sym_root="&ticker." and sym_suffix="&suffix."
                    and time_m >= &session_open.
                    and time_m <= &session_close.;
            run;
        %end;
        %else %put NOTE: No source file taqmsec.ctm_&day_name.;
    %end;
%mend;
%process_dates(%sysfunc(inputn(20241007,yymmdd8.)),
               %sysfunc(inputn(20241011,yymmdd8.)));
```

The daily-view example only selects the asset and session. Apply the complete
validated filters and measure calculation before treating its output as a
research dataset. Compare missing files with the trading calendar.

## Spreads and quote-rule classification

Input `matched_trades_quotes` must already contain the appropriate prevailing
or lagged NBBO for each trade, without future information. Use WRDS consolidated
trades where suitable; a custom match must maintain quote state as described in
`filters-and-methods.md`.

```sas
data spreads;
    set matched_trades_quotes;
    if bid > 0 and ask >= bid and price > 0;
    midquote = (bid + ask) / 2;
    quoted_spread = ask - bid;
    relative_spread = quoted_spread / midquote;
    effective_spread = 2 * abs(price - midquote);
    relative_effective = effective_spread / midquote;
    direction = .;
    if price > midquote then direction = 1;
    else if price < midquote then direction = -1;
run;
```

Midpoint trades remain unclassified here. Add the explicit tick-rule and lag
policy before describing this as a complete Lee-Ready implementation.
