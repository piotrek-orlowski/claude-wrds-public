-- All visible non-system relation metadata. Counts are pg_class rows,
-- never research-observation counts.
SELECT JSONB_BUILD_OBJECT(
    'collected_at', CURRENT_TIMESTAMP,
    'schema_name', n.nspname,
    'schema_usage', HAS_SCHEMA_PRIVILEGE(n.oid, 'USAGE'),
    'schema_comment', OBJ_DESCRIPTION(n.oid, 'pg_namespace'),
    'relation_count', COUNT(c.oid),
    'table_count', COUNT(*) FILTER (WHERE c.relkind IN ('r','p')),
    'view_count', COUNT(*) FILTER (WHERE c.relkind IN ('v','m')),
    'foreign_table_count', COUNT(*) FILTER (WHERE c.relkind = 'f'),
    'select_privilege_count', COUNT(*) FILTER (WHERE HAS_TABLE_PRIVILEGE(c.oid, 'SELECT'))
)
FROM pg_namespace n
JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind IN ('r','p','v','m','f')
WHERE n.nspname <> 'information_schema' AND n.nspname !~ '^pg_'
GROUP BY n.oid, n.nspname
ORDER BY n.nspname;
