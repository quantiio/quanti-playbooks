# Where things are — screens used by the migration

Give the path in words, one click at a time. When a video or image link exists below,
share it: a picture of the screen beats any description. Menus can be in the user's
language: translate the labels.

## Google Tag Manager

**Tell the WEB and SERVER containers apart.** At tagmanager.google.com, the container
list of the account shows a *Type* column: *Web* or *Server*. Both IDs look like
`GTM-XXXXXXX`. The WEB container is the one the site loads.

| What | Path | Media |
|---|---|---|
| Export a container (JSON) | Open the container → **Admin** → **Export container** → choose the published version → **Export** | — |
| Container config (SERVER) | SERVER container → **Admin** → **Container settings** → **Manually provision tagging server** → copy **Container config** | [video](https://quanti-docs-assets.s3.fr-par.scw.cloud/sgtm/gtm-container-config-20260917.mp4) |
| Server container URLs (SERVER) | SERVER container → **Admin** → **Container settings** → *Server container URLs* → **Add URL** | — |
| `server_container_url` (WEB) | WEB container → **Tags** → the Google tag (ID `G-…`) → **Configuration settings** → parameter `server_container_url` | — |
| Preview (SERVER) | SERVER container → **Preview** (top right) — always from here | — |
| Publish a previous version (rollback) | Container → **Versions** → the version before → **⋯** → **Publish** | — |

## The site's page source

In Chrome, Edge or Firefox, type `view-source:` in front of the site address (e.g.
`view-source:https://www.client.com`), then select all (Ctrl/Cmd + A), copy, and paste
into a text file to attach. On Safari, enable the Develop menu first.

## Network tab (live check)

Right click on the page → **Inspect** → **Network** tab → reload the page → type the
Quanti domain in the filter box. Requests should be there with status 200. A screenshot of
that list is enough.

## Quanti

| What | Where |
|---|---|
| Server-side servers | Quanti app → the project → **Server-side tagging** |
| Billable hits of a server | the server's page, *Billable hits* |
| Public guide | https://docs.quanti.io/server-side-tagging/setup-guide |
