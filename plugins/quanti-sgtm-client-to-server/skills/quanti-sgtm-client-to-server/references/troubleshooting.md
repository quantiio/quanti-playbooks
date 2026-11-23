# Troubleshooting — server-side setup with Quanti

Start with the symptom. Prefer a rollback to a fix under pressure: the site must keep
measuring while you look. Every step has its rollback in the playbook.

## DNS check fails (`check_dns`)

- **A CNAME is on the name**: remove it, then add the A and AAAA.
- **The AAAA is missing**: both are required; without it, IPv6 visitors never reach the
  server, silently.
- **Wrong name**: some DNS editors want `tag`, others `tag.client.com`. Compare with
  `full_name`.
- **Records right but pending**: propagation. Record `blocked`, come back later. Never delete
  and recreate the server for this.

## Server in `error`, or `starting` for more than 15 minutes

Show `status_message`. About DNS: `check_dns` (a certificate in error is requested again at
most every 10 minutes). Otherwise: Quanti support. **Never suggest recreating the server.**

## Preview shows nothing on the server

- Preview opened from an old link: open it again from Tag Manager.
- The server address is missing from *Server container URLs* (step 5).
- `server_container_url`: `https://` + domain, no trailing slash, no path.

## The request arrives but the GA4 tag does not fire

- The trigger is not *Client Name equals GA4*, or the GA4 client was renamed.
- The server container version with the GA4 tag is not published (step 5 publishes it).

## The Tag QUANTI: does not write

- Its trigger differs from the GA4 tag's: it only reads events of the GA4 client.
- *Allowed domains* excludes the domain you test on.
- The webhook is another Tag analytics webhook of the project: `inspect_sgtm_server`
  `status` → `consent_tag` gives the right one.
- Not visible yet: a hit may appear only once its session is closed (up to 30 minutes).

## Test and production differ by more than 1 % (step 9)

- An event tag was not duplicated to the test property, or duplicated twice.
- The test Google tag does not fire on every page (trigger not *Initialization – All Pages*).
- Consent: compare how each property's tags react to a refusal; they must behave the same.
- Filters or data settings differ between the two GA4 properties (internal traffic, data
  retention, referral exclusions).
Never switch production while the gap is unexplained.

## The site lost all its tags after the snippet change

- Snippet generated with the **SERVER** container ID: the server answers `400`. Put Google's
  snippet back, generate it again with the WEB container ID.
- URLs edited by hand: `404`. Paste it again as generated.
- Run `check_snippet.py` on the new page source.

## A rewritten path goes to a Google domain

The request is rejected by Google (`404`): the data is lost. Put Google's standard snippet
back and contact Quanti support with the page and the request.

## "A request to googletagmanager.com is still blocked"

Expected: `www.googletagmanager.com/td` is GTM telemetry, not measurement. No data lost, never
billed.

## "Is it immune to ad blockers now?"

No, never promise it. Their server's paths are specific to it, so public filter lists do not
recognise them, but some requests stay blockable on their parameters alone.
Details: https://docs.quanti.io/server-side-tagging

## The data dropped after a switch

1. Publish the previous WEB container version if the drop is clear and ongoing.
2. Server Preview: do GA4 requests arrive, does the GA4 tag fire?
3. Is the published WEB version the right one, with the server address on the production
   Google tag only?
4. Still unclear: Quanti support, with the switch time and the server's domain.
