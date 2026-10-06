-- Direct view dependencies with referenced columns. This is not a claim
-- that a one-target view is a lossless alias or that its data is accessible.
SELECT JSONB_BUILD_OBJECT(
    'source_oid', s.oid, 'source_schema', sn.nspname, 'source_relation', s.relname,
    'target_oid', t.oid, 'target_schema', tn.nspname, 'target_relation', t.relname,
    'referenced_column_numbers', JSONB_AGG(DISTINCT d.refobjsubid ORDER BY d.refobjsubid)
)
FROM pg_rewrite r
JOIN pg_class s ON s.oid = r.ev_class
JOIN pg_namespace sn ON sn.oid = s.relnamespace
JOIN pg_depend d ON d.classid = 'pg_rewrite'::regclass
                 AND d.objid = r.oid AND d.refclassid = 'pg_class'::regclass
JOIN pg_class t ON t.oid = d.refobjid AND t.oid <> s.oid
JOIN pg_namespace tn ON tn.oid = t.relnamespace
WHERE s.relkind IN ('v','m') AND t.relkind IN ('r','p','v','m','f')
  AND sn.nspname <> 'information_schema' AND sn.nspname !~ '^pg_'
GROUP BY s.oid, sn.nspname, s.relname, t.oid, tn.nspname, t.relname
ORDER BY sn.nspname, s.relname, tn.nspname, t.relname;
