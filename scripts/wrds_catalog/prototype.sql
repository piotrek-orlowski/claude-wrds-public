-- Metadata-only prototype. Do not scan research observations.
SELECT JSONB_BUILD_OBJECT(
    'collected_at', CURRENT_TIMESTAMP,
    'schema_name', n.nspname, 'relation_name', c.relname,
    'relation_oid', c.oid, 'relation_kind', c.relkind,
    'schema_usage', HAS_SCHEMA_PRIVILEGE(n.oid, 'USAGE'),
    'select_privilege', HAS_TABLE_PRIVILEGE(c.oid, 'SELECT'),
    'comment', OBJ_DESCRIPTION(c.oid, 'pg_class'),
    'columns', (SELECT JSONB_AGG(JSONB_BUILD_OBJECT(
         'ordinal', a.attnum, 'name', a.attname,
         'type', FORMAT_TYPE(a.atttypid, a.atttypmod),
         'not_null', a.attnotnull,
         'comment', COL_DESCRIPTION(c.oid, a.attnum)
       ) ORDER BY a.attnum)
       FROM pg_attribute a
       WHERE a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped),
    'dependencies', (SELECT JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT(
         'schema_name', tn.nspname, 'relation_name', tc.relname,
         'relation_oid', tc.oid,
         'schema_usage', HAS_SCHEMA_PRIVILEGE(tn.oid, 'USAGE'),
         'select_privilege', HAS_TABLE_PRIVILEGE(tc.oid, 'SELECT')
       )) FROM pg_rewrite r
       JOIN pg_depend d ON d.classid = 'pg_rewrite'::regclass
                         AND d.objid = r.oid
                         AND d.refclassid = 'pg_class'::regclass
       JOIN pg_class tc ON tc.oid = d.refobjid AND tc.oid <> c.oid
       JOIN pg_namespace tn ON tn.oid = tc.relnamespace
       WHERE r.ev_class = c.oid AND tc.relkind IN ('r','p','v','m','f'))
)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE (n.nspname, c.relname) IN (
    ('crsp','msf_v2'), ('crsp','ccmxpf_lnkhist'),
    ('comp','funda'), ('optionm','opprcd2024'))
ORDER BY n.nspname, c.relname;
