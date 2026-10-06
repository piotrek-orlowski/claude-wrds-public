# Query development and saved outputs

Use this reference when an extraction needs reusable SQL files or several joined sources. It carries the general query-project workflow formerly embedded in the orchestrator agent. Cross-database semantics live in [wrds-linking](../../wrds-linking/SKILL.md).

## Define the result

Record the universe, sample dates, observation frequency, desired output key, required measures, and when information must have been available. Distinguish a historical descriptive merge from a point-in-time strategy input. Resolve identifiers for the requested dates rather than treating a present-day ticker as permanent.

Test each source on the same small window, then test the complete join. Compare input and output counts, distinct keys, unmatched observations, overlapping links, units, NULLs, and boundary dates. Retain ambiguous matches for review; `DISTINCT` must not silently decide between conflicting links.

Use `EXPLAIN` for an initial plan review. `EXPLAIN ANALYZE` executes the query: use it only on the bounded pilot before considering larger runs. Adding `LIMIT` after an aggregate does not make the aggregate cheap.

## File organization

Follow an existing project layout. For a new query project, use only the directories needed:

```text
queries/
  crsp/        # CRSP extracts
  comp/        # Fundamentals
  optionm/     # Option extracts
  merged/      # Cross-database queries
  lib/         # Shared identifier, date, and filter logic
scripts/       # Optional local processing
output/        # Data outputs; follow the project's data/versioning policy
docs/          # Data dictionary and validation notes
```

Keep local TAQ SAS programs under the project's data/task directory and mirror that subdirectory in WRDS scratch as specified by the SSH skill.

Give saved SQL a short header documenting:

- Purpose and source tables, including product version.
- Parameters and units; state whether placeholders are psql variables or application bind parameters.
- Output key, columns, units, and date alignment.
- Filters, link validity rules, and availability/lags.
- Dependencies, extraction date, and pilot validation.

Do not run illustrative `:parameter` or `{year}` placeholders without binding/replacing them correctly. Quote data values using the query runner's parameter mechanism; validate dynamic identifiers such as year-suffixed table names.

## Scale and hand off

Export in bounded date or asset batches. Preserve the query, requested parameters, actual row counts, exclusions, and the extraction date alongside each data product. Validate the first batch before completing the sample. Download only the required processed results from TAQ jobs.

Return the output paths, reproduction command, observed data coverage, and any unresolved validation limits. A command completing successfully does not itself prove economic correctness or complete coverage.

Use Git only when the user's task or project instructions authorize it. When a commit is requested, stage the intended SQL and documentation, exclude restricted data according to project rules, and describe the substantive change. Query execution does not itself require a commit.
