# Quanti — move your server-side GTM to Quanti

Claude guides you, step by step, through moving an existing server-side Google Tag
Manager setup — hosted by another provider or by yourself — to a server hosted by Quanti,
on your own domain. You keep the same server container, the same tags and the
same data; only the host changes.

## What you need

- Admin access to the WEB and SERVER containers in Google Tag Manager.
- Someone who can add DNS records on your site's domain.
- A Quanti account and project, with a server-side tagging seat available.

## Use it

Install the plugin, connect the bundled Quanti connector from the plugin's *Connectors*
tab, then tell Claude: "I want to move my server-side GTM to Quanti". Claude audits your
current setup from your container exports, helps you choose how to switch, walks you
through the DNS records and the Tag Manager settings, tests before any visitor is switched,
and checks the data the next day. It takes about an hour of work over two days. You can
stop at any time and resume in a new conversation.

## What it sends, and where

- **Your files stay in the conversation.** The container exports and page source you
  attach are read by scripts bundled with the plugin; secrets they may contain (API tokens)
  are never displayed.
- **The Quanti connector** reads and creates your server-side server in your Quanti
  project, with your own Quanti account.
- **Your progress is saved in your Quanti account**: the steps you went through, their
  status, and short notes on why a step was blocked. This lets you resume later and helps
  Quanti see where users get stuck. No domain, container ID or personal data is stored in
  the notes.

## Support

Quanti documentation: https://docs.quanti.io/server-side-tagging — or contact Quanti
support from the Quanti app.
