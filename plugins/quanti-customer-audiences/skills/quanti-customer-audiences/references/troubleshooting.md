# Troubleshooting — customer audiences

Say what you checked, then the likely cause, then one action. State a cause only when a
tool or the user showed it.

## `create_aggregation_view` refuses the view or the procedure

- A BigQuery error about the view's query (a function, a clause, a join "not supported
  in materialized views"): expected for some audiences. Go to step 9 (procedure); do
  not change the audience's rule to make the view pass.
- *columns is required when creating a materialized view*: pass the 7 columns.
- *name must start with 'llm_'* / *must target the 'quanti_agg' dataset*: the procedure is
  `quanti_agg.llm_aud_<name>`, nothing else.
- *run_daily: …*: the message says what to fix. The table the procedure writes must be
  `quanti_agg.llm_aud_<name>_list`, not named like the procedure, and `columns` must
  describe it.
- *maximum number of aggregation views reached (20)*: delete an unused audience first
  (SKILL.md, *Delete an audience*). Do not reuse another audience's name.
- *not available on Snowflake*: audiences need a BigQuery project. Stop there.
- A SQL error: run the step 6 `SELECT` alone with `execute_query` to find it, fix, retry.

## The view is behind

A view is recomputed every 12 hours by BigQuery, not at a fixed hour. If the orders of
yesterday are missing, wait for the next recomputation; the send of the following day
catches up.

## Procedure: the table `llm_aud_<name>_list` does not exist

1. `list_aggregation_views`: the procedure must show `run_daily: true`. If not, it was
   created or recreated without it: recreate it with `run_daily: true` (step 9).
2. Ask the user to open the *Aggregation Views* connector in Quanti and to tell you (or
   paste a screenshot of) its last run. No run yet: **Sync now**. A failed run shows the
   error of each procedure that failed:
   - *Not found: Table …* in the procedure: the query reads a table that does not exist;
     run the step 6 `SELECT` with `execute_query` to find it.
   - *Access Denied*: Quanti's access to the project's BigQuery is missing a right. The
     user contacts Quanti support from the app.

## The audience is much smaller on the platform than in the table

Normal up to a point: the platform shows the people it recognised, not the emails sent.
Check, in this order: emails hashed in the table (they must not be: step 6), the `email`
field mapped to the email column, and for Google the consent fields (people sent with
`denied` are not used).

## The audience emptied on the platform

Mirror mode: the source was empty at the time of the send. `execute_query` a count on it
today, then check the hours: the reverse connector after the *Aggregation Views*
connector (procedure), itself after the orders connectors. Fix the hours; the next send
refills it.

## A successful send with 0 rows

The connector ran before the audience was recomputed, or the source was empty. Same
checks as above.

## The quota is refused

Say « Vous n'avez pas assez de quota sur votre offre Quanti » (in the user's language)
with the two ways out: add Activate units in the billing space, or delete a reverse
connector no longer used. No workaround.
