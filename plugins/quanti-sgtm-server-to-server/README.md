# Quanti — move your server-side GTM to Quanti

Claude guides you, step by step, through moving an existing server-side Google Tag
Manager setup — hosted by another provider or by yourself — to a server hosted by Quanti,
on a new subdomain of your site. Your server container is copied as is into a new one;
your current host keeps running until the end, as your way back.

## What you need

- Tag Manager access to the WEB container and the current SERVER container, with the
  right to publish, and the right to create a container.
- GA4 (Editor), Google Ads and Meta Events Manager (read).
- Someone who can add DNS records on your site's domain.
- The developer who will replace the GTM snippet of your site on the switch day.
- A way to place a test order.
- A Quanti project with a server-side tagging seat available.

## Use it

Install the plugin, connect the bundled Quanti connector from the plugin's *Connectors*
tab, then tell Claude: "I want to move my server-side GTM to Quanti". Claude takes an
inventory of your current setup, measures a reference, creates the Quanti server with you,
copies your server container into a new one, adds the Quanti tag that writes your events
to your data warehouse, tests every event in Preview before any visitor is switched, then
guides the switch in two reversible moves and watches your data for at least 72 hours.

Count two to three hours of work over about a week. In Claude Desktop or Cowork, Claude
can use its built-in browser (you sign in yourself); on claude.ai, it works from your
screenshots and files. You can stop at any time and resume in a new conversation.

## What it sends, and where

- **Your files stay in the conversation.** Container exports and page sources are read by
  scripts bundled with the plugin; secrets they may contain (API tokens) are never shown.
- **Claude never publishes, never changes DNS, never edits your site.** It tells you what
  to do; you or your developer do it.
- **The Quanti connector** creates your server and the webhook of the Quanti tag in your
  Quanti project, and reads your data warehouse for the checks, with your own account.
- **Your progress is saved in your Quanti account**: the steps, their status, and short
  notes on why a step was blocked. No domain, container ID or personal data in the notes.

## Support

Quanti documentation: https://docs.quanti.io/server-side-tagging — or contact Quanti
support from the Quanti app.
