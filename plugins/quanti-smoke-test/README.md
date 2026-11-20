# Quanti — smoke test (staging)

Internal test plugin, not meant for clients. It checks that a Quanti plugin works in
claude.ai, Claude Desktop and Cowork before the real migration plugins are written.

## Use it

Install the plugin, connect the bundled "quanti-stg" connector from the plugin's
Connectors tab, then ask Claude to "run the Quanti smoke test". Claude runs a bundled
script on a sample Google Tag Manager export, calls the Quanti staging connector, draws a
diagram, and ends with a table of results to send to the Quanti team.

## Data

The script reads only the sample export, or an export you attach. The connector call
lists your Quanti staging projects; only their number is shown.
