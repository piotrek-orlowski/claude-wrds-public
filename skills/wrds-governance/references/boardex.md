# BoardEx and Altrata: people, roles, and networks

## Product and access boundaries

[WRDS BoardEx products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/boardex/),
retrieved 2026-10-05, lists both the BoardEx and Altrata Executive & Company
product families, each split into North America, Europe, UK, and Rest of World.
Both have current weekly product updates. Treat them as distinct schemas;
similar labels do not establish interchangeable IDs or field semantics.

The 2026-10-05 local permission/planning evidence is narrower than that directory:

| Route | Observed access evidence |
|---|---|
| `boardex.na_*`, `boardex.row_*` | 42 tables each accepted by bounded planning probes |
| `boardex.eur_*`, `boardex.uk_*` | 42 tables each denied by product guards |
| `boardsmp.jr_*` | 40 trial/sample tables accepted |
| `altrata.{na,eur,row,uk}_*` | All 156 alias tables denied by product guards |
| `altrata_exec_samp` / `altsamp` alias | 35 sample tables accepted; aliases are not additional independent datasets |

Planning acceptance is not a completed data extraction. Check the individual
table in `wrds-catalog`, then prototype one company and a short role window.
Underlying product schemas include `boardex_na`, `boardex_row`, and
`boardex_trial`; do not replace accessible guarded aliases with an underlying
schema that lacks USAGE permission.

## BoardEx column-backed routes

Use `wrds-catalog` `table boardex.na_wrds_org_composition` or search the desired
concept. The 2026-10-05 column metadata verifies:

| Table | Fields to retain |
|---|---|
| `boardex.na_wrds_org_composition` | `companyid`, `directorid`, `rolename`, `seniority`, `datestartrole`, `dateendrole`, start/end date flags |
| `boardex.na_dir_profile_emp` | `primarykeyid`, `directorid`, `companyid`, `rowtype`, `brdposition`, `rolename`, `ned`, `leadershipteam`, role dates and date flags |
| `boardex.na_dir_profile_details` | `directorid`, `dob`, `dobflag`, `dod`, `dodflag`, `gender`, `nationality`, `age` |
| `boardex.na_wrds_company_profile` | `boardid`, `cikcode`, `ticker`, `isin`, `countryofquote`, `primarystock`, predecessor/successor/ultimate-parent company IDs |
| `boardex.na_dir_profile_education` | `primarykeyid`, `directorid`, `companyid`, `awarddate`, `awarddateflag`, `qualification` |
| `boardex.na_wrds_individual_networks` | `dirbrdid`, `directorid`, `companyid`, `associationtype`, role fields, `overlapyearstart`, `overlapyearend`, integer overlap-year counterparts |

`directorid` and `companyid` are separate concepts. Company-profile `boardid`
is another named key to verify against the requested company mapping; do not
join every numeric ID merely because types coincide. The inspected IDs are
stored as double precision: preserve integral identifier values without
rounding, scientific-notation text conversion, or name-based deduplication.

Build an as-of composition from role spells overlapping the requested date.
Read `datestartroleflag`/`dateendroleflag`: column comments identify them as
disclosed-date flags, but do not enumerate the codes. Verify code meanings
before imputing incomplete dates or treating year 9999 as an actual end date.
Keep the native date and flag in outputs. A person's current `age` is not age
at an old observation date; use disclosed birth information with its precision
flag when historical age is required.

Network rows have relationship and overlap dimensions. Define whether a link
means common employer, education, another association, or an active overlap at
the as-of date. Count distinct people/edges after applying that definition;
raw row counts can count multiple roles and relationship types repeatedly.

## Altrata sample workflow

The inspected `altrata_exec_samp.role` contains string identifiers
`role_id`, `person_id`, `organization_id` (`varchar(18)`), dates
`role_start_date`/`role_end_date`, `role_current_prior_status`, `role_type`,
and executive/non-executive/leadership flags stored as strings. Preserve them
as strings and inspect actual code values. Join sample roles to sample `per`
and `org` on their native keys after checking uniqueness. Do not combine them
with BoardEx numeric IDs or regional full Altrata tables by position or name.

The full alias `altrata.na_role` and the sample role layout already differ:
`role_type` is in the inspected sample layout, while the inspected full alias
definition omits it. Do not write a generic full/sample SELECT from memory.

## Validation and documentation

Check one-company spell overlaps, multiple simultaneous roles, date precision,
person-to-company cardinality, repeated security listings, and unmatched
company IDs before constructing a larger panel. Preserve region and full/sample
status. A current career history does not establish historical public knowledge
of every role or relationship.

[WRDS Introduction to BoardEx](https://wrds-www.wharton.upenn.edu/pages/grid-items/introduction-to-boardex/)
is the public overview landing page. The
[official BoardEx overview](https://wrds-www.wharton.upenn.edu/pages/support/manuals-and-overviews/boardex/wrds-overview-boardex-data/)
redirected to login on 2026-10-05, so its contents and date-flag codes were not
verified. Use the precise current manual when a flag's meaning is material.
