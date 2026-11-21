# Quanti — customer audiences for Meta and Google Ads

Claude helps you turn your customers' orders into an advertising audience: recent buyers
to exclude from acquisition campaigns, customers to win back, buyers of one product to
offer another, your best customers as a lookalike seed. Claude writes and checks the
query, Quanti recomputes the audience every night and sends it to Meta and Google Ads.
You do not need to know SQL.

## What you need

- A Quanti project whose data warehouse is **BigQuery**, with your orders in it (from a
  Quanti connector or from your own tables), including the customer's email.
- Access to the **BigQuery console** of that project. It is not always needed: only for
  some audiences, to set up their nightly recomputation once (Claude gives you what to
  paste), and to delete an audience.
- Access to the Meta and/or Google Ads ad accounts that will receive the audience.
- One Activate unit of your Quanti plan per audience and per platform.

## Use it

Install the plugin, connect the bundled Quanti connector from the plugin's *Connectors*
tab, then tell Claude: "I want to create an audience of my customers". Claude asks who
you want to target, finds your orders, shows you the audience and its quality before
anything is created, then sets up the daily send to Meta or Google Ads with you. Count
about an hour, plus a check the next day after the first send. You can stop at any time and resume in a new conversation.

## What it sends, and where

- **Your customers' data stays in your data warehouse.** Claude reads counts and a few
  sample rows to check the audience, with emails partly masked in the conversation.
- **The Quanti connector** creates, in your project, the view (or procedure) that keeps
  the audience up to date and the connector that sends it, with your own Quanti account. Emails are
  hashed by Quanti before they are sent to Meta or Google.
- **Your progress is saved in your Quanti account**: the steps you went through, their
  status, and short notes on why a step was blocked. No email, audience content or
  personal data is stored in the notes.

## Support

Quanti documentation: https://docs.quanti.io — or contact Quanti support from the Quanti
app.
