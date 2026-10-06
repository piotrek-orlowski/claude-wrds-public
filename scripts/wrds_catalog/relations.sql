-- Visible relation metadata only; no observation counts or data scans.
SELECT JSONB_BUILD_OBJECT(
    'relation_oid', c.oid,
    'schema_name', n.nspname,
    'relation_name', c.relname,
    'relation_kind', c.relkind,
    'schema_usage', HAS_SCHEMA_PRIVILEGE(n.oid, 'USAGE'),
    'select_privilege', HAS_TABLE_PRIVILEGE(c.oid, 'SELECT'),
    'comment', OBJ_DESCRIPTION(c.oid, 'pg_class'),
    'view_definition', CASE WHEN c.relkind IN ('v','m') AND n.nspname !~ '^taq'
                            THEN PG_GET_VIEWDEF(c.oid, TRUE) ELSE NULL END
)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r','p','v','m','f')
  AND n.nspname <> 'information_schema' AND n.nspname !~ '^pg_'
ORDER BY n.nspname, c.relname;
