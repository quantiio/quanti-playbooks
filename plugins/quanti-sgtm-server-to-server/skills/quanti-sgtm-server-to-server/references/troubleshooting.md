# Troubleshooting — server-side GTM migration to Quanti

Start with the symptom the user describes. Always prefer a rollback to a fix under
pressure: the site must keep collecting while you look. The current host keeps running
until the very end: it is the rollback.

## Rollback: which change to undo

The script and the server address are two independent changes. The script decides where
`gtm.js` loads from; `server_container_url` decides where hits go. Undo the one at fault:
- **No tag fires at all**, `gtm.js` in error in the Network tab: the script. The developer
  puts the previous snippet back (or Google's standard one, which always works).
- **`gtm.js` loads but hits fail**, or the new server's tags error: publish the previous WEB
  container version (Versions → the one before → ⋯ → Publish). Hits go back to the current
  host; the new script can stay while you look.
Safe only while the current host runs and its server container is unchanged since the
export.

## Common traps

- **Cancelling the current host too early.** Until the observation is over it is the only
  rollback, and cached pages may call it for a few days.
- **Changing the current server container during the migration.** The copy becomes wrong:
  export again, or apply the change in both containers.
- **Importing into the wrong container.** An Overwrite import into the current host's
  container erases production. Check the container ID at the top of Tag Manager.
- **Publishing the test workspace by mistake.** In test, you run Preview; you never click
  Submit on the "Switch to Quanti" workspace before the switch.
- **A forgotten place holding the old address** (second Google tag, settings variable,
  constant, custom HTML): the traffic is split between the two servers. Step 3's list.
- **Improving while migrating** (cookie settings, a new platform, renaming the dataLayer):
  any gap becomes impossible to explain. Copy as is, switch, then improve.
- **Switching at the wrong time**: Friday, before a public holiday, a sales peak, or with
  the developer and the publisher not available together.

## DNS check fails (`check_dns`)

Fix in that order:
- **A CNAME is on the name**: remove it, then add the A and AAAA. A name cannot have a
  CNAME and other records at once.
- **The AAAA is missing**: both are required. Without it, visitors on IPv6 networks never
  reach the server, and nothing shows it.
- **Wrong name**: some DNS editors want `tag`, others `tag.client.com`. Compare with
  `full_name` in the records.
- **Records right but still pending**: propagation. Record `blocked`, come back later.
  Never delete and recreate the server for this.

## Server in `error`

Show `status_message`. About DNS: run `check_dns` (a certificate in error is requested
again, at most every 10 minutes). Otherwise: Quanti support. **Never suggest deleting and
recreating the server.**

## Status stays `starting`

Up to 15 minutes is normal on first start. Beyond, the server goes to `error`: see above.

## Preview shows nothing on the new server container

- Open Preview **from Tag Manager**, never from an old link: an old link sends the hits to
  a session nobody watches.
- The new server address must be in *Server container URLs* of the NEW container (step 6):
  an import does not copy it.
- `server_container_url` in the WEB workspace: `https://` + domain, no trailing slash, no
  path, and changed in **every** place step 3 found.

## Tags fire on the current host but not on the new server

- The request is not claimed by any client: compare the clients with the inventory. A
  request no client claims gets a `404` and is not forwarded.
- A template that depends on the current host (`old_host_dependencies`) does not work
  elsewhere: find what it did; the person who set up the container, or Quanti support.

## The Tag QUANTI: does not write

- It only reads events from the GA4 client: its trigger must be the imported GA4 tag's.
- *Allowed domains* excludes the domain you test on: add it, or empty the field.
- The webhook URL is another Tag analytics webhook of the project, not the one included
  in the server: `inspect_sgtm_server` `status` → `consent_tag`.
- The hit is just not visible yet: it may appear only once its session is closed (up to
  30 minutes). Wait before concluding.

## The site lost all its tags after the snippet change

- The snippet was generated with the **SERVER** container ID: the server answers `400`.
  Roll back the script, generate it again with the WEB container ID.
- The snippet's URLs were edited by hand: a variation answers `404`. Paste it as generated.
- Run `check_snippet.py` on the new page source to see what the page really loads.

## "A request to googletagmanager.com is still blocked"

Expected. GTM's own script calls `www.googletagmanager.com/td` directly; it is GTM
telemetry, not measurement. Blocking it loses no data and it is never a billable hit.

## "Is it immune to ad blockers now?"

No, and never promise it. The paths of their server are specific to it, so public filter
lists do not recognise them, but some requests stay blockable on their parameters alone.
Details: https://docs.quanti.io/server-side-tagging

## The data dropped after the switch (step 11)

1. Publish the previous WEB container version if the drop is clear and ongoing.
2. Check the server container Preview: do GA4 requests arrive, do the tags fire?
3. Check that every place holding the server address was changed, and that the published
   WEB version is the right one.
4. Look at the current host's console: a steady flow there means a forgotten place.
5. Still unclear: Quanti support, with the switch time and the server's domain.
