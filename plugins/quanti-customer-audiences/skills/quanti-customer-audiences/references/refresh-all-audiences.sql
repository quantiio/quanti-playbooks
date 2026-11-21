-- Quanti audiences: recompute every audience of this project, every night.
-- Runs each procedure quanti_agg.llm_aud_* one after the other. A new audience created
-- with Claude is picked up automatically: this query never needs to change.
-- If one audience fails, the others still run, and the scheduled query is then marked
-- as failed with the names of the audiences that were not recomputed.
DECLARE failed ARRAY<STRING> DEFAULT [];

FOR proc IN (
  SELECT routine_name
  FROM quanti_agg.INFORMATION_SCHEMA.ROUTINES
  WHERE STARTS_WITH(routine_name, 'llm_aud_')
  ORDER BY routine_name
)
DO
  BEGIN
    EXECUTE IMMEDIATE FORMAT('CALL `quanti_agg.%s`()', proc.routine_name);
  EXCEPTION WHEN ERROR THEN
    SET failed = ARRAY_CONCAT(failed, [proc.routine_name]);
  END;
END FOR;

IF ARRAY_LENGTH(failed) > 0 THEN
  RAISE USING MESSAGE = FORMAT('Audiences not recomputed: %s', ARRAY_TO_STRING(failed, ', '));
END IF;
