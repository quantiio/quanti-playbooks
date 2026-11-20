# Troubleshooting — server-side GTM migration to Quanti

Start with the symptom the user describes. Always prefer a rollback to a fix under
pressure: the site must keep collecting while you look.

## Rollback, in one line per strategy

- **A (new subdomain)**: publish the previous WEB container version (Versions → the one
  before → Publish) and restore the previous snippet. The old host is still running.
- **B (same subdomain)**: put the old DNS records back. Visitors return to the old host
  as their DNS refreshes.

## DNS check fails (`check_dns`)

Read what `check_dns` says and fix in that order:
- **A CNAME is still on the name** (often the old host's): remove it, then add the A and
  AAAA. A name cannot have a CNAME and other records at once.
- **The AAAA is missing**: both are required. Without it, visitors on IPv6 networks never
  reach the server, and nothing shows it.
- **Wrong name**: some DNS editors want `tag`, others `tag.client.com`. Compare with
  `full_name` in the records.
- **Records right but still pending**: propagation. Wait, record the step `blocked`, come
  back later. Never delete and recreate the server for this.

## Server in `error`

Show `status_message` to the user. If it is about DNS, run `check_dns` (a certificate in
error is requested again, at most every 10 minutes). Otherwise: Quanti support. **Never
suggest deleting and recreating the server.**

## Status stays `starting`

Up to 15 minutes is normal on first start. Beyond, the server goes to `error`: see above.

## Preview shows nothing on the server container

- Open Preview **from Tag Manager**, never from an old link or bookmark: each preview
  session has its own identifier, an old link sends the hits to a session nobody watches.
- The Quanti URL must be in *Server container URLs* (step 9).
- `server_container_url` in the WEB container: `https://` + domain, no trailing slash, no
  path. Check it in the WEB container Preview (Tag Assistant), on the Google tag.

## The site lost all its tags after the snippet change

- The snippet was generated with the **SERVER** container ID instead of the WEB one: the
  server answers `400`. Roll back, generate it again with the WEB container ID (step 3).
- The URLs of the snippet were edited by hand: the paths are specific to the server and
  container, a variation answers `404`. Paste it again as generated.
- Run `check_snippet.py` on the new page source to see what the page really loads.

## Hits arrive but some tags do not fire

- A request that no **client** of the server container claims gets a `404`, is not
  forwarded and not billed. Compare the clients with the audit of step 3.
- A template listed in `old_host_dependencies` at step 3 calls the old host's domains: it
  stops working once the old host is cancelled, or right at the switch. Find which tag uses
  it and what it did; this is a question for the person who set up the old container, or
  for Quanti support.

## "A request to googletagmanager.com is still blocked"

Expected. GTM's own script calls `www.googletagmanager.com/td` directly; it is GTM
telemetry, not measurement. Blocking it loses no data and it is never a billable hit. Tell
the user before they find it alone.

## "Is it immune to ad blockers now?"

No, and never promise it. The paths and container ID of their server are specific to it, so
public filter lists do not recognise them, but some requests stay blockable on their
parameters alone. Details: https://docs.quanti.io/server-side-tagging

## The GA4 data dropped after the switch (step 13)

1. Rollback if the drop is clear and ongoing.
2. Check the server container Preview: do GA4 requests arrive, does the GA4 tag fire?
3. Check that every Google tag of the WEB container got the new `server_container_url`
   (the audit lists them all), and that the published version is the right one.
4. Still unclear: Quanti support, with the switch time and the server's domain.
