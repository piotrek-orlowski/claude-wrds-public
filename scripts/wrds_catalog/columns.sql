-- psql variable catalog_schemas is a JSON array of schema names.
-- Deduplicate identical column layouts within each schema on the server.
WITH selected_relations AS MATERIALIZED (
    SELECT c.oid, n.nspname
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r','p','v','m','f')
      AND n.nspname IN (SELECT JSONB_ARRAY_ELEMENTS_TEXT(:'catalog_schemas'::jsonb))
), relation_columns AS (
    SELECT r.oid, r.nspname,
           COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT(
               'ordinal', a.attnum, 'name', a.attname,
               'type', FORMAT_TYPE(a.atttypid, a.atttypmod),
               'not_null', a.attnotnull,
               'comment', COL_DESCRIPTION(r.oid, a.attnum)
           ) ORDER BY a.attnum) FILTER (WHERE a.attnum IS NOT NULL), '[]'::jsonb) AS columns
    FROM selected_relations r
    LEFT JOIN pg_attribute a ON a.attrelid = r.oid AND a.attnum > 0 AND NOT a.attisdropped
    GROUP BY r.oid, r.nspname
)
SELECT JSONB_BUILD_OBJECT('schema_name', nspname, 'columns', columns,
                         'relation_oids', JSONB_AGG(oid ORDER BY oid))
FROM relation_columns
GROUP BY nspname, columns
ORDER BY nspname, MIN(oid);
