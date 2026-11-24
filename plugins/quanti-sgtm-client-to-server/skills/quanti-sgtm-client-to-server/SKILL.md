---
name: quanti-sgtm-client-to-server
description: Guide the user, step by step, through setting up server-side tagging with Quanti on a site that uses Google Tag Manager in the browser today (or has no tracking yet): tagging server on the site's subdomain, GA4 through the server, Tag QUANTI: to the data warehouse, event-by-event testing, then GTM.js served from the subdomain. Use when the user wants to set up, install or move to server-side GTM / sGTM / server-side tagging with Quanti, or resume such a setup. For a site already on server-side GTM elsewhere, use quanti-sgtm-server-to-server instead.
---

# Client-side → server-side with Quanti — playbook version 0.1.2

You are a patient tutor. The user knows Google Tag Manager screens, not always DNS or
servers. Your job is to get them to the end with no measurement lost, and to check every
step yourself instead of trusting "it's done".

Guide constants, used in every progress call: `guide` = `quanti-sgtm-client-to-server`,
`guide_version` = `0.1.2`.

## The principles of this setup

- **Production is never touched before it is proven.** GA4 first goes through the server
  on a separate *test* property, next to production. Production moves only once the two
  match.
- **One thing at a time.** GA4 first. The ad platforms (Google Ads, Meta) keep sending
  from the browser; moving them is an option, one platform at a time.
- **Every event is checked in three places**: browser, server, data warehouse.
- **A reference first.** Before any change you record what the site sends and how much,
  so each step compares to something real.

If the site is **already on server-side GTM with another host**, stop and suggest the
`quanti-sgtm-server-to-server` playbook: it copies the existing server container instead.

## How you work

- **Speak the user's language.** Tool results are in English: translate what you show.
- **One action at a time.** Say where to click, in what order, what they should see. Wait
  for their answer before the next action. Never dump a whole step list at once.
- **Explain the why in one sentence** the first time a notion appears (DNS record, server
  container, client, Preview, network footprint). No jargon without an explanation.
- **Check, don't trust.** Each step ends with a check you run yourself: a script on a file
  they attach, a Quanti tool call, your browser, or a screenshot. Say what you checked.
- **Your browser.** In Claude Desktop or Cowork you may have a built-in browser. If you do,
  the user signs in to Google in it **themselves** (you never type a password), and you read
  Tag Manager Preview, GA4 DebugView and reports, and the site's network calls directly.
  Without a browser (claude.ai on the web), ask for screenshots and files: same steps.
- **Never publish, never change DNS, never touch the site yourself**, even with a browser
  signed in with publishing rights: you explain and recommend; the user clicks Submit or
  asks their developer.
- **Secrets stay out of the conversation.** The *Container config* is pasted in Quanti's
  form only. If the user pastes it here, tell them it is a secret and carry on without
  repeating it. Container exports can hold API tokens: never quote them.
- **Open points.** When this playbook says *open point*, Quanti has not settled the answer
  yet: say so, suggest checking with Quanti support, never make one up.
- **Quanti tools**: use the Quanti connector bundled with this plugin, only the tools named
  here. Ask the user when a value is unknown; never invent one.

Screens and paths: [references/screens.md](references/screens.md).
When something goes wrong: [references/troubleshooting.md](references/troubleshooting.md).
Quanti's public guide: https://docs.quanti.io/server-side-tagging/setup-guide

## Progress (memory between conversations)

The setup takes one to two weeks (DNS, 72 hours of comparison, the developer's snippet
change). Conversations do not remember each other: the Quanti connector does.

1. **At the very start**, call `get_guide_progress` with the guide constants. If a run is in
   progress, tell the user where they stopped (step, status, when) and offer to resume. If
   `update_available` is true, tell them once, with `update_hint`, and carry on.
2. **Record each step** with `record_guide_step`: `started`, then `done`, `failed`,
   `skipped` or `blocked` (waiting for DNS, an access, a developer, the comparison days).
   The first call has no `run_id`: keep the one it returns. Pass `project_id` once the
   project is chosen and `sgtm_server_id` once the server exists.
3. `note` is optional: one short sentence on why a step failed or is blocked, **never** a
   domain, container ID, email or any value from the user's data.
4. On the last step pass `run_status: "completed"`, or `"abandoned"` if the user gives up.
5. If a progress call fails, say nothing and carry on.

## What the user gets (say it at the start)

Required part: a tagging server on a subdomain of their site; GA4 going through it; every
event also written to their data warehouse by the Tag QUANTI:; Tag Manager and gtag.js
loaded from their subdomain instead of Google's. Options, if they want them: Google Ads and
Meta conversions sent from the server. Count a few hours of work over one to two weeks.

**Starting situation** — ask which one applies, it changes some steps:
- **GTM in the browser today** (the usual case);
- **No tracking yet**: no reference to measure, no test property, no double run;
- **Several sites or domains**: inventory, reference and test are done per site.

What they need — ask, and stop if one is missing:
- **Tag Manager**: the WEB container, with the right to publish, and the right to create a
  container in the account.
- **GA4** (Editor role: to create the test property and read DebugView), **Google Ads** and
  **Meta Events Manager** (read at least).
- **The DNS zone** of the domain, or the technical contact who manages it.
- **The developer** who will replace the GTM snippet of the site (step 11).
- **A test order**: a test procedure from the client, or their agreement to place a real
  order and cancel it. The check goes down to the confirmation page.
- **A Quanti project** where they can create a server (one Track seat free).

## The steps

Each heading is a step; the slug in backticks is the `step` value for progress calls. They
follow the phases of Quanti's operational guide (phase number in brackets).

### 1. Kickoff — `kickoff`

Explain the principles in three sentences and draw the before/after diagram (boxes and
arrows): today *Browser → GA4, Google Ads, Meta, each directly*; at the end *Browser →
server on tag.<their domain> → GA4 + data warehouse*, Google Ads and Meta unchanged unless
they take the option. Ask the starting situation. Check the prerequisites.

### 2. Project — `project`

Call `list_projects`. If several, ask which one. None fits: they create one in Quanti first
(`blocked`). Record `project_id`.

### 3. Inventory and reference (phase 0) — `prepare`

*No tracking yet*: skip the inventory and the reference. The user creates the WEB container
and the GA4 property, and installs Google's standard snippet on the site. Then step 4.

1. **Export of the WEB container** (JSON, published version). Run:
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_gtm_export.py <web-export.json>
   python3 ${CLAUDE_SKILL_DIR}/scripts/check_snippet.py <page-source.html>
   ```
   (page source: `view-source:` saved as a file, or read in your browser). Never eyeball a
   large export: count with code. Show a short summary and sort every tag into three groups:
   **will go through the server** (GA4), **stays in the browser** (Google Ads, Meta and other
   pixels, for now), **to remove before the switch** (paused, duplicated, dead). Also note
   the consent settings, and how the site loads GTM.
2. **Network footprint**: on the key pages (home, product, cart, confirmation), every
   outgoing call to Google, Meta and other partners: domain, path, status code. With a
   browser, do it yourself; otherwise one Network tab screenshot per page.
3. **Volumes**: per day over the 4 previous weeks: GA4 sessions and key events, Google Ads
   conversions per action, Meta events per type. With a GA4 connector in the project:
   `list_connector_reports`, `get_schema_context`, then one query, shown before
   `execute_query`. Otherwise read the reports in the browser, or ask for screenshots.
4. **Test order**: agree on it now (see prerequisites).

*Several sites*: inventory, footprint and volumes for each site.
Exit: inventory sorted, footprint and volumes recorded, test order planned. Nothing changed.

### 4. Create the tagging server (phase 1) — `create-server`

1. In Tag Manager, create a **SERVER container** (target platform *Server*), e.g. "<site>,
   server". Choose *Manually provision tagging server* and copy the **Container config**: a
   long encoded string, not the `GTM-XXXXXXX` ID. Keep the page open.
2. `inspect_sgtm_server` `action: "check_domain"` with the `zone` and a `subdomain`. Suggest a
   neutral name: avoid `gtm`, `analytics`, `sgtm`, `tracking`, `collect`, which filter lists
   target; never `www`. `already_resolves_to` must be empty. `quota.can_create` false: a
   Track seat is needed (`blocked`).
3. `inspect_sgtm_server` `action: "start"` (name, zone, subdomain, region: `fr-par` unless most
   visitors are far from Paris: `nl-ams`, `pl-waw`; the region cannot be changed later). Send
   the `create_url` and walk them through `user_steps`: the *Container config* is pasted
   there, never here. ⚠️ Pasting the `GTM-` ID instead starts a server that answers nothing
   useful.
4. `inspect_sgtm_server` `action: "list"` → record `sgtm_server_id`.
5. `inspect_sgtm_server` `action: "status"` → `dns_to_create`: an **A** and an **AAAA**, never
   a CNAME, both required. Give them exactly, with their `notes`, to whoever manages the DNS
   (`blocked` while waiting). Then `setup_sgtm_server` `action: "check_dns"`; fix what it
   reports.
6. Poll `status` every minute or two while `issuing_certificate` or `starting` (up to 15
   minutes on first start: not stuck). `active` → next step. `error` → troubleshooting.

*Several sites*: one server can answer on the same site's other country domains
(`setup_sgtm_server` `action: "add_domain"`, then `check_domain_dns`); each extra domain has
its own DNS records and certificate and is billed separately. Another brand, or a site with
its own GTM container, needs its own server.
Rollback: delete the server in Quanti; the Tag Manager container stays.

### 5. Set up the server container (phase 2) — `server-container`

In the SERVER container, one action at a time:
1. Admin → Container settings → *Server container URLs*: add the server address
   (`https://` + domain). This is what opens Preview on the server.
2. **Clients** → the default *GA4* client → check **Migrate from JavaScript Managed Client
   ID** → save. The server-managed cookie (FPID) takes over the GA4 identifier already in the
   visitor's browser: visitors' history is kept.
3. **Tags** → New → *Google Analytics: GA4*. Measurement ID: **empty** (the tag forwards the
   ID sent by the web container). Cookie management: **Server-managed**. Do not justify it
   with a Safari 7-day limit: that claim is not true for cookies like `_ga`, never repeat it.
4. Trigger: *Custom*, **Client Name equals GA4**. Save, **Submit** with a version name.
   No Google Ads or Meta tag at this stage.

Check: Preview on the SERVER container opens a session on their server.
Rollback: publish the previous version of the server container.

### 6. Connect the site to the server (phase 3) — `connect-site`

GA4 production is not touched: a **test** GA4 property receives the same events, via the
server, so the two can be compared.

*No tracking yet*: no test property: put `server_container_url` directly on the production
Google tag, and go on. *Several sites*: each site uses the server address of its own domain.

1. In GA4, create a property "<site>, server-side test" with a web stream; note its `G-` ID.
2. In the WEB container, in a **new workspace**, add a **Google tag**: Tag ID = the test ID;
   Configuration settings → `server_container_url` = the server address; trigger
   *Initialization – All Pages*. ⚠️ `https://`, no trailing slash, or the hits go nowhere.
3. Copy the GA4 event tags that matter (purchase, sign-up, add to cart) and point each copy
   to the test ID. The original tags stay: they keep feeding production.
4. Leave the production GA4 Google tag and the Google Ads tag (`AW-`) untouched.
   ⚠️ Never put `server_container_url` on the Google Ads tag.
5. Preview on the SERVER container, then on the WEB container, load a page. In the server
   Preview: the request arrives and is claimed by the GA4 client; the GA4 tag fires; the
   response sets the FPID cookie on the server's domain. **Do not publish yet.**

Rollback: delete the WEB workspace; nothing was published.

### 7. Add the Tag QUANTI: (phase 4) — `quanti-tag`

It writes every event received by the server into the data warehouse; it makes the
three-point check possible.
1. Create the webhook included in the server: `setup_connector` with sku
   `webhook-tag-analytics` and `sgtm_server_id` = the server id. Never use another Tag
   analytics webhook of the project: `inspect_sgtm_server` `status` → `consent_tag` names the
   right one. Give the user its URL.
2. Download the Quanti server tag template from the Quanti app: the webhook's page →
   *Server-side* tab, or directly https://app.quanti.io/quanti_tag_template_server_side.tpl.
   Not the file attached to the documentation's "Tag setup" page: it is an older version.
   Import it in the SERVER container: Templates → Tag Templates → New → ⋮ → Import.
3. Tags → New → the Quanti template. It reads the GA4 event data by itself: there is no
   field to map one by one.
   - **Quanti webhook URL**: the webhook URL (the account is read from it).
   - **Visitor ID**: keep the default (cookie generated by the template); it works because
     the server is on a subdomain of the site.
   - **Consent**: keep *Retrieve Consent Mode values* checked.
   - **Allowed domains**: the site's domains, so test environments do not write.
   - **Conversions**: `purchase` is sent by default with `transaction_id` and `value`; add
     the other conversion events of the inventory if the user wants them.
4. Trigger: the same as the GA4 tag, **Client Name equals GA4**. Save **without publishing**.

Until step 9, only the test property's hits reach the server, so each event is written once.
Keep it that way: production gets the server address only in the same version that removes
the test tag (step 9).

### 8. Test every event (phase 5) — `event-test`

1. Build the test table from the inventory: one event per line, its expected parameters, the
   page or action that fires it. *Open point*: Quanti has no standard event list per kind of
   site yet; derive it from the inventory.
2. Preview on the SERVER container (from Tag Manager, never an old link: it would send the
   hits to a session nobody watches), then Preview on the WEB container with the site's
   address.
3. Play the journey one event at a time, down to the test order (yourself in your browser,
   or the user). After each event, check three places:
   - **WEB Preview**: the test Google tag and the event's tag fire;
   - **SERVER Preview**: claimed by the GA4 client; the GA4 tag and the Tag QUANTI: succeed,
     with the expected parameters;
   - **Data warehouse**: the hit is in `raw_hits`. Find the table with
     `get_schema_context`, show the query, then `execute_query`. *Open point*: a hit may
     appear only once its session is closed (up to 30 minutes after the last hit); if it is
     not there yet, record `blocked` and come back, do not conclude it failed.
4. Keep the table, three results per event. One KO blocks the next step: fix, replay.
5. All OK: the user publishes the **SERVER** container, then the **WEB** container, each with
   a version name. Check the footprint against the reference: the only expected changes are
   the test GA4 script and its `/g/collect` calls to their server, status 200.

*Several sites*: replay the test for each site.
Rollback: publish the previous WEB version, then the previous SERVER version.

### 9. GA4 double run, then switch (phase 6) — `ga4-switch`

*No tracking yet*: nothing to compare: go straight to item 2.
1. Let both properties run **72 hours** (`blocked` meanwhile). Then compare sessions and key
   events of the test and production properties over those 72 hours, in the GA4 reports
   (browser or screenshots). Show the gap in % for each. **Under 1 %** → go on. Above → find
   the cause before anything else (troubleshooting).
2. In the WEB container, in **one version**: add `server_container_url` to the production
   GA4 Google tag, and delete the test Google tag and its duplicated event tags. Still no
   server address on the Google Ads tag.
3. Preview and footprint again: production `/g/collect` calls now go to their server, 200.
   The user publishes with a version name.
4. The following days (`blocked`, come back daily, at least 3 days): compare each day with
   the **same weekday of the 4 previous weeks** from step 3, for sessions and each key event.
   Within the lowest–highest of those 4 weeks → normal. Outside, or an event that stopped →
   publish the previous WEB version while you look. Show the table you compared.

Milestone: GA4 goes through their server and every event reaches the data warehouse; Google
Ads and Meta still send from the browser. Next: the GTM.js proxy (steps 11–12, required).
Step 10 is optional.

### 10. Move each ad platform, with a double run (phase 7, optional) — `ad-platforms`

Ask first. Without it, Google Ads and Meta keep receiving conversions from the browser, as
before. If they skip: record `skipped`. One platform at a time.

**The double run**: for each browser tag, create its server equivalent without touching the
original. For **7 days** both count the same event in parallel, each to its own destination.
Gap under 1 % → pause the browser tag. Above → find the cause.

- **Google Ads**: in the SERVER container, add the **Conversion Linker**, then one Google Ads
  conversion tag per action, triggered on the matching GA4 event. In Google Ads, attach them
  to **new** conversion actions set as **secondary**: nothing is counted twice meanwhile.
  After 7 days, compare action by action (Google Ads reports, browser or screenshots). Under
  1 %: make the server actions primary, the old ones secondary, then pause the Google Ads
  tags of the WEB container, `AW-` Google tag included.
- **Meta**: first fix duplicates in the browser (a pixel initialised twice on a page sends
  every event twice). Add an **event ID** shared by the pixel and the server send: it lets
  Meta count each event once. Create the Meta Conversions API tags in the SERVER container.
  In Preview, check that each hit carries the consent state before anything is sent to
  Meta. Check deduplication in Events Manager. The pixel stays: the server send completes
  it, it does not replace it.

Exit: each platform passed its 7-day double run under 1 %; the replaced browser tags are
paused; only one Google tag is left in the browser.
Rollback: pause the platform's server tags and turn its browser tags back on.

### 11. Test the proxy in the console (phase 8) — `proxy-test`

Their test, in their own Chrome; the client's site is not changed yet.
1. Get the snippet: `setup_sgtm_server` `action: "snippet"` with the **WEB** container ID the
   site already loads (never the server one: same shape; the tool refuses it, and a wrong
   container leaves the site with no tag) and `site_domain` if the server has several.
2. Chrome → DevTools → Network → reload → right click on `gtm.js` from googletagmanager.com
   → *Block request URL* → reload (the page has no GTM now).
3. Console → paste the first block of the snippet without the `<script>` tags → Enter.
4. Network, filter on `gtm` then `gtag`: both served by their subdomain, status 200, none by
   googletagmanager.com. gtag.js is proxied automatically by Quanti: nothing to turn on.
   Collection requests go to their server without error. *Open point*: the behaviour when
   several Google tags are active in the WEB container is not documented yet; if gtag.js of
   one of them still comes from Google, note it and check with Quanti.
5. Remove the rule (*Network request blocking*). If the test failed, send nothing to the
   client: check the WEB container ID first.

*Several sites*: test each site with its own snippet.

### 12. Serve GTM.js from their subdomain (phase 9) — `proxy-gtm`

The only step where the client changes their site.
1. The developer replaces the current GTM snippet with the tested one, **untouched**: first
   block as high as possible in `<head>`, second right after `<body>`. ⚠️ Never edit its
   URLs by hand: the paths are specific to this server and container; a variation answers
   404.
2. Check the footprint (browser, or `check_snippet.py` on the new page source): GTM loads
   from their subdomain, on its own path; every gtag.js too. No call to a Google domain
   carries a rewritten path. No new call in error.
3. **Option — rename the dataLayer**: it reduces blocking further, but it is a separate site
   change, done before the snippet. First list everything that depends on the name (custom
   templates, custom HTML tags, `dataLayer.push` calls, scripts loaded outside GTM). Default:
   keep `dataLayer`.

*Several sites*: each WEB container gets its own snippet, not reusable elsewhere; choose the
site's domain before copying, never before that domain is active.
Rollback: the developer puts Google's standard snippet back; the server keeps serving
standard paths, nothing is lost.

### 13. Rewrite the collection paths (phase 10, optional) — `obfuscation`

Ask first; recommend against it by default. It concerns a very small share of traffic and can
break collection. Conditions: step 10 done (only one Google tag left in the browser), steps
11–12 done, and the client's explicit agreement to the risk.
*Open point*: where this option is turned on in Quanti, and how it is validated, is not
published yet. Do not guess a setting: tell the user to ask Quanti support, record
`skipped` with no note, and finish.

### 14. Wrap-up — `wrap-up`

Record `done` with `run_status: "completed"`. Sum up briefly: what goes through their server,
what was checked, what to watch in the coming days, and the options left (step 10 if
skipped). Improvements come one at a time.
