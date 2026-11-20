---
name: quanti-smoke-test
description: Run the Quanti plugin smoke test. Use when the user says "smoke test", "test the Quanti plugin", "quanti-smoke-test", or asks whether the Quanti plugin works in this app.
---

# Quanti plugin smoke test — version 0.1.1

You are checking that a Quanti plugin works in the app the user is in. Run the five
checks below in order, without asking for confirmation between them. Do not stop at the
first failure: record it and move on. End with the report table described at the end.

## Check 1 — Plugin version

Tell the user: "Smoke test plugin version **0.1.1** is loaded." This value is used to
check how updates reach users: when the plugin is updated, this number changes.

## Check 2 — Bundled script execution

Run the bundled script on the sample GTM container export:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_gtm_export.py ${CLAUDE_SKILL_DIR}/assets/sample-gtm-export.json
```

- PASS if the script prints a JSON summary with `"ok": true`.
- FAIL otherwise. Report exactly what happened: code execution unavailable, path not
  resolved, Python missing, script error (paste the error).

Do not imitate the script by reading the JSON yourself: the point is to know whether the
script runs. If the user has attached their own GTM export (a `.json` file), run the same
script on that file too and show its summary.

## Check 3 — Bundled Quanti connector

Call the Quanti connector's `list_projects` tool (the connector bundled with this plugin
is named `quanti-stg`; in some apps it appears as "Quanti Stg").

- PASS if the tool answers, even with an empty list. Show the number of projects only,
  not their names.
- FAIL if no Quanti tool is available (the user probably has not connected it yet: tell
  them to open Customize > Plugins > this plugin > Connectors and connect it), or if the
  call returns an error (paste it).
- Also note whether you see the Quanti tools **twice** (for example two `list_projects`
  from two different connectors). That is the duplicate-connector check.

## Check 4 — Diagram

Draw this flow as a simple diagram (an artifact or an inline SVG, whatever this app
supports best):

Browser → Server-side GTM on the client's own domain → GA4 / Meta / Google Ads

- PASS if a diagram renders. Say which form you used.

## Check 5 — Environment

Report, as far as you can tell: the app (claude.ai web, Claude Desktop chat, Cowork),
whether you have a code execution sandbox, and the value of `${CLAUDE_SKILL_DIR}` if you
could resolve it.

## Report

End with one table, one row per check: check, PASS or FAIL, one-line detail. Then one
sentence: "Send this table to the Quanti team."
