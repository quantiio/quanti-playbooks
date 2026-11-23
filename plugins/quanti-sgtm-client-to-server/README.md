# Quanti — set up server-side tagging

Claude guides you, step by step, through moving a site that uses Google Tag Manager in the
browser (or has no tracking yet) to server-side tagging with Quanti, on a subdomain of your
site. Your production measurement is only switched once a test property has proven the new
path.

## What you need

- Tag Manager access to the site's WEB container, with the right to publish, and the right
  to create a container.
- GA4 (Editor), Google Ads and Meta Events Manager (read).
- Someone who can add DNS records on your site's domain.
- The developer who will replace the GTM snippet of your site.
- A way to place a test order.
- A Quanti project with a server-side tagging seat available.

If your site already runs server-side GTM with another host, use the
`quanti-sgtm-server-to-server` plugin instead.

## Use it

Install the plugin, connect the bundled Quanti connector from the plugin's *Connectors* tab,
then tell Claude: "I want to set up server-side tagging with Quanti". Claude takes an
inventory of your container, measures a reference, creates the server with you, routes a
test GA4 property through it, adds the Quanti tag that writes your events to your data
warehouse, checks every event in three places, compares test and production for 72 hours
before switching, then has Tag Manager served from your subdomain. Moving Google Ads and
Meta to the server is offered as an option.

Count a few hours of work over one to two weeks. In Claude Desktop or Cowork, Claude can use
its built-in browser (you sign in yourself); on claude.ai, it works from your screenshots
and files. You can stop at any time and resume in a new conversation.

## What it sends, and where

- **Your files stay in the conversation.** Container exports and page sources are read by
  scripts bundled with the plugin; secrets they may contain are never shown.
- **Claude never publishes, never changes DNS, never edits your site.** It tells you what to
  do; you or your developer do it.
- **The Quanti connector** creates your server and the webhook of the Quanti tag in your
  Quanti project, and reads your data warehouse for the checks, with your own account.
- **Your progress is saved in your Quanti account**: the steps, their status, and short notes
  on why a step was blocked. No domain, container ID or personal data in the notes.

## Support

Quanti documentation: https://docs.quanti.io/server-side-tagging — or contact Quanti support
from the Quanti app.
