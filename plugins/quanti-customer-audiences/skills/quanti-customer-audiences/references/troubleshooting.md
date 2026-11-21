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
- *maximum number of aggregation views reached (20)*: delete an unused audience first
  (SKILL.md, *Delete an audience*). Do not reuse another audience's name.
- *not available on Snowflake*: audiences need a BigQuery project. Stop there.
- A SQL error: run the step 6 `SELECT` alone with `execute_query` to find it, fix, retry.

## The view is behind

A view is recomputed every 12 hours by BigQuery, not at a fixed hour. If the orders of
yesterday are missing, wait for the next recomputation; the send of the following day
catches up.

## Procedure: the table `audiences.<name>` does not exist the next morning

1. `list_scheduled_queries`: is `Quanti - refresh audiences` active, and did it run? A
   failed run names, in its error, the audiences that were not recomputed.
2. Ask the user to run `CALL quanti_agg.llm_aud_<name>();` in the BigQuery console and
   to paste the error, if any:
   - *Not found: Dataset … audiences*: the dataset was not created (step 8).
   - *… was not found in location …*: the dataset `audiences` is not in the same location
     as the orders tables. It must be recreated in the right location (empty it first).
   - *Access Denied*: the account running the scheduled query cannot read the orders or
     write in `audiences`. The project's BigQuery administrator fixes the access.

## Procedure: the table is not offered in Quanti's source picker (step 12)

- It does not exist yet: a table appears only once computed (step 10).
- It is in another location than the project's other datasets.
- The dataset is named like an internal or aggregation dataset (`*_agg`): use `audiences`.

## The audience is much smaller on the platform than in the table

Normal up to a point: the platform shows the people it recognised, not the emails sent.
Check, in this order: emails hashed in the table (they must not be: step 6), the `email`
field mapped to the email column, and for Google the consent fields (people sent with
`denied` are not used).

## The audience emptied on the platform

Mirror mode: the table was empty at the time of the send. `execute_query` a count on the
table today, then check that the connector's `sync_hour` is after the scheduled query and
that the orders connectors finished before it. Fix the hours; the next send refills it.

## A successful send with 0 rows

The connector ran before the table was recomputed, or the table was empty. Same checks
as above.

## The quota is refused

Say « Vous n'avez pas assez de quota sur votre offre Quanti » (in the user's language)
with the two ways out: add Activate units in the billing space, or delete a reverse
connector no longer used. No workaround.
