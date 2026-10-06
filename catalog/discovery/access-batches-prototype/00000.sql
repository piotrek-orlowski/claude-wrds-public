DO $catalog_2290839548fbb0b9$
DECLARE
    item jsonb;
    guard text;
    permitted boolean;
    result jsonb;
    message text;
    code text;
    checked timestamptz;
BEGIN
    FOR item IN SELECT value FROM jsonb_array_elements('[{"error_wrapper":false,"guard_relations":["altrata_exec_eur.eur_announce"],"relation_name":"eur_announce","relation_oid":"2199112922","schema_name":"altrata"},{"error_wrapper":false,"guard_relations":["comp_na_daily_all.funda"],"relation_name":"funda","relation_oid":"2199233950","schema_name":"comp"},{"error_wrapper":false,"guard_relations":["crsp_a_ccm.ccmxpf_lnkhist"],"relation_name":"ccmxpf_lnkhist","relation_oid":"2786561790","schema_name":"crsp"},{"error_wrapper":false,"guard_relations":["crsp_a_stock.msf_v2"],"relation_name":"msf_v2","relation_oid":"3746509749","schema_name":"crsp"},{"error_wrapper":false,"guard_relations":[],"relation_name":"msf_v2","relation_oid":"843972920","schema_name":"crsp_a_stock"},{"error_wrapper":true,"guard_relations":[],"relation_name":"acti","relation_oid":"883587154","schema_name":"crspa"},{"error_wrapper":false,"guard_relations":["optionm_all.opprcd2024"],"relation_name":"opprcd2024","relation_oid":"3767763966","schema_name":"optionm"}]'::jsonb)
    LOOP
        checked := clock_timestamp();
        result := jsonb_build_object(
            'relation_oid', item->'relation_oid',
            'schema_name', item->>'schema_name',
            'relation_name', item->>'relation_name',
            'checked_at', checked,
            'method', 'select_limit0_and_observed_alias_guards',
            'guard_relations', item->'guard_relations',
            'status', 'planning_accepted',
            'zero_row_status', 'not_run',
            'guard_status', 'not_present',
            'runtime_wrapper_status', 'not_run',
            'sqlstate', NULL, 'error', NULL);
        BEGIN
            EXECUTE format('SELECT * FROM %I.%I LIMIT 0',
                           item->>'schema_name', item->>'relation_name');
            result := result || jsonb_build_object('zero_row_status', 'accepted');
            IF jsonb_array_length(item->'guard_relations') > 0 THEN
                result := result || jsonb_build_object('guard_status', 'accepted');
            END IF;
            FOR guard IN SELECT jsonb_array_elements_text(item->'guard_relations')
            LOOP
                BEGIN
                    SELECT pg_catalog.has_table_privilege(guard, 'SELECT') INTO permitted;
                    IF NOT permitted THEN
                        result := result || jsonb_build_object(
                            'status', 'guard_denied', 'guard_status', 'false',
                            'error', 'Observed alias privilege guard returned false');
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    GET STACKED DIAGNOSTICS message = MESSAGE_TEXT, code = RETURNED_SQLSTATE;
                    result := result || jsonb_build_object(
                        'status', 'guard_denied', 'guard_status', 'error',
                        'sqlstate', code, 'error', message);
                END;
            END LOOP;
            IF (item->>'error_wrapper')::boolean THEN
                BEGIN
                    EXECUTE format('SELECT * FROM %I.%I LIMIT 1',
                                   item->>'schema_name', item->>'relation_name');
                    result := result || jsonb_build_object(
                        'method', 'select_limit0_and_error_wrapper_limit1',
                        'runtime_wrapper_status', 'accepted');
                EXCEPTION WHEN OTHERS THEN
                    GET STACKED DIAGNOSTICS message = MESSAGE_TEXT, code = RETURNED_SQLSTATE;
                    result := result || jsonb_build_object(
                        'method', 'select_limit0_and_error_wrapper_limit1',
                        'status', 'runtime_error', 'runtime_wrapper_status', 'error',
                        'sqlstate', code, 'error', message);
                END;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS message = MESSAGE_TEXT, code = RETURNED_SQLSTATE;
            result := result || jsonb_build_object(
                'status', CASE WHEN code = '42501' THEN 'permission_denied' ELSE 'planning_error' END,
                'zero_row_status', 'error', 'sqlstate', code, 'error', message);
        END;
        result := result || jsonb_build_object(
            'duration_ms', round(extract(epoch from (clock_timestamp()-checked))*1000, 3));
        RAISE NOTICE 'CATALOG_PROBE %', result::text;
    END LOOP;
END
$catalog_2290839548fbb0b9$;
