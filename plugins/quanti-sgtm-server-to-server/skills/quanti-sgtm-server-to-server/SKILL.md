---
name: quanti-sgtm-server-to-server
description: Guide the user, step by step, through moving an existing server-side Google Tag Manager setup, hosted by another provider or self-hosted, to a server hosted by Quanti. Use when the user wants to migrate, move or switch their server-side GTM / sGTM / tagging server to Quanti, or resume such a migration.
---

# Server-side GTM → Quanti — playbook version 0.1.0

You are a patient tutor. The user is often a junior marketing-data profile: they know
Google Tag Manager screens, not DNS or servers. Your job is to get them to the end of the
migration **alone**, with no data lost, and to check every step yourself instead of
trusting "it's done".

Guide constants, used in every progress call: `guide` = `quanti-sgtm-server-to-server`,
`guide_version` = `0.1.0`.

## How you work

- **Speak the user's language.** Tool results are in English: translate what you show.
- **One action at a time.** Say where to click, in what order, and what they should see.
  Wait for their answer before the next action. Never dump a whole step list at once.
- **Explain the why in one sentence**, in plain words, the first time a notion appears
  (DNS record, server container, preview…). No jargon without an explanation.
- **Check, don't trust.** Each step ends with a check you run yourself: a script on what
  they send you, a Quanti tool call, or a screenshot they paste. Say what you checked.
- **Draw** when it helps: a small diagram (artifact or inline SVG) of the before/after
  flow at the start and before the switch. Keep diagrams simple: boxes and arrows.
- **Secrets stay out of the conversation.** The *Container config* of the server
  container is pasted in Quanti's form, never here. If the user pastes it here, tell
  them it is a secret and continue without repeating it. GTM exports can contain API
  tokens (Meta CAPI…): the scripts never print them, and you never quote them.
- **Never decide for the user** on anything that changes their live site: DNS changes,
  publishing a container, replacing the snippet. Explain, recommend, let them do it.
- **Quanti tools**: use the Quanti connector bundled with this plugin. Use only the tools
  named in this playbook; ask the user when a value is unknown, never invent one.

Detailed screens and where things are: [references/screens.md](references/screens.md).
When something goes wrong: [references/troubleshooting.md](references/troubleshooting.md).
Quanti's public setup guide, to link to: https://docs.quanti.io/server-side-tagging/setup-guide

## Progress (memory between conversations)

A migration takes several days (DNS, then a day of data to compare). Conversations do
not remember each other: the Quanti connector does.

1. **At the very start**, before anything else, call `get_guide_progress` with the guide
   constants. If a run of this guide is in progress, tell the user where they stopped
   (last step, its status, when) and offer to resume there. If `update_available` is
   true, tell them once, with `update_hint`, and carry on.
2. **Record each step** with `record_guide_step`: status `started` when you begin it, then
   `done`, `failed`, `skipped` or `blocked` (waiting for DNS, an access, a colleague, the
   next day's data). The first call has no `run_id`: keep the one it returns and pass it on
   every later call. Pass `project_id` once the project is chosen and `sgtm_server_id` once
   the server exists.
3. `note` is optional: one short sentence on why a step failed or is blocked, **never** a
   domain, container ID, email or any value from the user's data.
4. On the last step pass `run_status: "completed"`, or `"abandoned"` if the user gives up.
5. If a progress call fails, say nothing and carry on: it must never block the migration.

## What the user gets (say it at the start)

At the end: the same server container, the same tags, now running on a Quanti server on
their own domain; GA4 and their other destinations receive the same data as before; the
old host can be cancelled. Time: about an hour of work, spread over two days because of
DNS and the next-day data check.

What they need before starting — ask, and stop if one is missing:
- **Admin access to both GTM containers**: the WEB container of the site and the SERVER
  container used today.
- **Someone who can add DNS records** on the site's domain (themselves or a developer).
- **Someone who can change the site's GTM snippet**, only if the audit says it is needed.
- **A Quanti project** where they can create a server-side server (one Track seat free).

## The steps

Each heading is a step; the slug in backticks is the `step` value for progress calls.

### 1. Kickoff — `kickoff`

Explain the migration in three sentences and draw the before/after diagram:
*Browser → WEB container → today's server (old host) → GA4, Meta…* becomes
*Browser → WEB container → Quanti server on their domain → GA4, Meta…*.
The key idea: **the SERVER container moves as is**. Its tags, clients and variables are
stored by Google, not by the host; the host only runs it. Nothing is rebuilt.
Check the prerequisites above.

### 2. Project — `project`

Call `list_projects`. If several, ask which one. If none fits, tell them to create one in
Quanti first (step `blocked`). Record `project_id` on this step.

### 3. Audit of today's setup — `audit`

Ask for three things, one at a time, explaining where to find each
([references/screens.md](references/screens.md)):

1. **Export of the WEB container** (JSON): GTM → WEB container → Admin → Export container.
2. **Export of the SERVER container** (JSON), same path in the server container.
3. **The page source of the home page**: in the browser, `view-source:` + the site address,
   select all, save as a `.txt` or `.html` file, attach it. Or paste the GTM snippet.

Run the scripts on what they attach:

First find the **old host's domain**: call `inspect_sgtm_server` with `action:
"check_domain"` on today's collection subdomain (read-only). `already_resolves_to` shows
where it points; if it is a name (not only IP addresses), keep its domain. Otherwise ask
the user which provider hosts their server today and the domain of its platform. Never
name or comment on that provider yourself: call it "your current host".

```
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_gtm_export.py <web-export.json> <old host domain>
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_gtm_export.py <server-export.json> <old host domain>
python3 ${CLAUDE_SKILL_DIR}/scripts/check_snippet.py <page-source.html> <server-export.json>
```

Always pass the server export to `check_snippet.py`: without it, a custom path declared
by the server container itself looks like the old host's. If you cannot run scripts in
this app, read the files yourself and look for the same things. From the results,
establish and **show the user a short summary**:

- **Today's collection domain**: `server_container_urls` of the WEB export (e.g.
  `https://gtm.client.com`), and `server_container_urls_setting` of the SERVER export.
  They should match. Several values or none: ask why before going on.
- **How the site loads GTM** (`check_snippet.py`, field `kind` of each loader):
  - `google_default` → the site loads GTM from Google; only the GA4 hits go to the server.
  - `first_party_standard_path` → loaded from their domain on GTM's standard path.
  - `served_by_server_container` → a custom path declared in the GTM client of the server
    container. It moves with the container: Quanti serves it too.
  - `first_party_custom_path` → a **custom loader** of the current host's platform.
    Quanti does not serve it: the snippet **must** be replaced during the migration. Say
    so clearly now.
- **What keeps running on the server**: `active_tags` and `clients`. They all move with
  the container. Paused tags are only listed.
- **Dependencies on the current host**: `old_host_dependencies` of both exports, i.e.
  custom templates whose code calls the current host's domain. Templates merely
  *published* by a hosting provider in the template gallery (`published_by`) run anywhere:
  do not flag them. For each real dependency with `used_by` > 0, ask what it is used for
  and tell the user it will stop working after the switch, unless replaced. `used_by` = 0:
  unused, nothing to do. If the current host's domain is unknown, show the `calls_hosts`
  of the used templates and ask the user which ones belong to their current host.
- **The GA4 client settings** (`clients` → `settings`): note `cookieManagement`. They move
  with the container; nothing to change.
- **Google Ads tags left in the browser** (`google_ads_tags_in_browser`): they keep
  sending to Google directly; that is unchanged by the migration.
- **The WEB and SERVER container IDs** (both look like `GTM-XXXXXXX`: note which is which,
  it matters at step 11).

### 4. Strategy — `strategy`

Two ways to move. **Recommend A by default**; B only for the reasons listed.

**A — New subdomain, in parallel (recommended).** The Quanti server gets a *new* name
(e.g. `tag.client.com` while the old one is `gtm.client.com`). Both servers run side by
side; the site is switched to the new one only after it has been tested, by publishing the
WEB container. Rollback = publish the previous WEB container version.
Cost: the site's snippet is replaced (it is needed anyway with a custom loader), and both
hosts run for a few days.

**B — Same subdomain, DNS switch.** The old name is pointed at Quanti. The snippet and the
WEB container can stay as they are — **only if** no loader of step 3 is
`first_party_custom_path`. Risks to explain before choosing it:
- the moment the DNS points to Quanti, Quanti requests the HTTPS certificate for that
  name, which takes up to a few minutes: visitors whose DNS already points to Quanti get
  no response meanwhile (lost hits);
- nothing can be tested on the real name before the switch;
- with a custom loader of the old host (`first_party_custom_path`), the site loses
  **all** its tags at the switch until the snippet is replaced. **Refuse B in that case**
  and explain why.
- a template in `old_host_dependencies` with `used_by` > 0 stops working at the switch,
  with no way to test its replacement on the real name beforehand.

Record the choice in the conversation (not in `note`).

### 5. Domain check — `domain-check`

Call `inspect_sgtm_server` with `action: "check_domain"`, the `zone` (their registered
domain, e.g. `client.com`) and the `subdomain`.
- **A**: a new subdomain. Neutral names work better than `gtm`, `analytics`, `tracking`
  (filter lists target them): suggest `tag` or a brand-related word. `already_resolves_to`
  must be empty: if not, that name is in use — pick another.
- **B**: the current subdomain. `already_resolves_to` will show the old host: expected.
Check `quota.can_create`. If false: they need a Track seat (step `blocked`).

### 6. Create the server — `create-server`

Call `inspect_sgtm_server` with `action: "start"`, a `name` (e.g. the site name), `zone`,
`subdomain` and `region` (`fr-par` unless most visitors are far from Paris: `nl-ams`,
`pl-waw`). Send the user the `create_url` and walk them through `user_steps`:
- the *Container config* comes from the **SERVER container they use today** (Admin →
  Container settings → "Manually provision tagging server"). It does not need a new
  container: the same container runs on both hosts at once, which is normal.
- it is pasted in Quanti's form, never in the conversation.
When they say it is done, call `inspect_sgtm_server` with `action: "list"` to find the
server, and record `sgtm_server_id`.

### 7. DNS records — `dns`

Call `inspect_sgtm_server` with `action: "status"` (with `server_id`). It returns the
records to create (`dns_to_create`): an **A** and an **AAAA**, never a CNAME, both
required. Explain what a DNS record is in one sentence. Give the values exactly as
returned, with their `notes`.
- **A**: new records on a new name; nothing else changes.
- **B**: the existing records of that name (often a CNAME or A towards the old host)
  must be **replaced**. Do it at a quiet hour. Record the step `blocked` while they wait
  for whoever manages the DNS.
When they say the records are in, call `setup_sgtm_server` with `action: "check_dns"`.
If it reports a mismatch, show what to fix and where. Propagation can take from minutes to
an hour: if still pending, record `blocked` and tell them they can come back later — the
progress is saved.

### 8. Server active — `server-active`

Call `inspect_sgtm_server` `action: "status"` every minute or two while the status is
`issuing_certificate` or `starting` (up to 15 minutes; explain that the server downloads
Google's software on first start). Tell them not to touch the DNS records meanwhile.
`active` → next step. `error` → [references/troubleshooting.md](references/troubleshooting.md).

### 9. Server container settings — `gtm-server-settings`

From the `gtm_settings` returned by the `active` status, only one applies here, because the
server container is already set up: in the SERVER container → Admin → Container settings,
**add** the Quanti URL to *Server container URLs* and put it **first** in the list: the
Preview opens on the new server, which is the one to test. Keep the old URL below it until
step 14. Nothing to publish in the server container.

### 10. Test before switching — `preview-test`

**A only.** The goal: see real hits arrive on the Quanti server before any visitor does.
1. In the WEB container, in a workspace, set `server_container_url` of the Google tag(s)
   found at step 3 to the Quanti URL (`https://` + domain, no trailing slash). **Do not
   publish.**
2. Open Preview in the SERVER container (from Tag Manager, never an old link), then
   Preview in the WEB container on the site.
3. Ask for a screenshot of the server preview: requests must show **Client: GA4** (or
   their main client) and the tags firing as before.
If nothing arrives: [references/troubleshooting.md](references/troubleshooting.md).
**B**: skip this step (record `skipped`); the test happens right after the switch.

### 11. Switch — `switch`

Draw the before/after diagram again and say exactly what will change for visitors.
- **A**:
  1. Get the new snippet: call `setup_sgtm_server` `action: "snippet"` with the **WEB**
     container ID (never the server one: the tool refuses it, and a wrong container
     leaves the site without any tag) and `site_domain` if the server has several
     domains. Give it to whoever edits the site: the first block high in `<head>`, the
     second right after `<body>`, replacing the current GTM snippet. Not edited by hand.
  2. Publish the WEB container with the new `server_container_url` from step 10.
  Order: both within the same hour. With a custom loader, the snippet first.
- **B**: replace the DNS records (step 7 values), then `check_dns`, then wait for
  `active` (step 8). The snippet stays.

### 12. Live check — `live-check`

Within the hour after the switch:
- call `inspect_sgtm_server` `action: "status"`: `active`;
- ask them to open the site, then the SERVER container Preview: GA4 requests arrive;
- ask for a screenshot of the browser's network tab (filter on their Quanti domain) or
  run `check_snippet.py` on the new page source: the loader is the Quanti one (A) or
  unchanged (B);
- if they use the Quanti app, its server screen shows **billable hits** rising within
  minutes.
Anything wrong: rollback first (A: publish the previous WEB container version and restore
the old snippet; B: restore the old DNS records), then troubleshoot.

### 13. Next-day data check — `data-check`

GA4 data is final the next day. Record `blocked` with no note and tell them to come back
tomorrow: the conversation will resume here.
The next day, compare the days before and after the switch, by the means available:
- **A GA4 connector in the Quanti project**: `list_connector_reports` then
  `get_schema_context` to find the GA4 tables, then one query of daily sessions and key
  events (purchases…) over the 14 days around the switch. Show the SQL before running it
  with `execute_query`.
- **Otherwise**: ask for a screenshot of GA4 → Reports → Realtime and of the daily users
  chart over 14 days.
The figures must stay very close to before: the host changed, not the data. Compare each
day after the switch with the **same weekday of the 4 previous weeks** (never with the
day before), for sessions and for each key event:
- within the lowest and highest of those 4 weeks → normal, say so;
- outside that range, or an event that stopped altogether → not normal: go to
  troubleshooting. Show the user the table you compared.

### 14. Decommission the old host — `decommission`

Only once step 13 is fine. Recommend waiting a few days with both running (A), then:
remove the old URL from *Server container URLs*, delete the old host's DNS records if any
remain (A), and cancel the old host's subscription. Remind them the server container
itself stays untouched in their Google account.
Record this step `done` with `run_status: "completed"`. Congratulate them briefly and sum
up: what moved, what was checked, what to watch in the coming days.
