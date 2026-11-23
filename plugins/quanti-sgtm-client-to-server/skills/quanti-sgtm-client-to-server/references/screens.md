# Where things are — screens used by the setup

Give the path in words, one click at a time. When a video link exists below, share it.
Menus can be in the user's language: translate the labels.

## Google Tag Manager

**Tell the WEB and SERVER containers apart.** At tagmanager.google.com, the container list
shows a *Type* column: *Web* or *Server*. Both IDs look like `GTM-XXXXXXX`. The WEB container
is the one the site loads.

| What | Path | Media |
|---|---|---|
| Export a container (JSON) | Container → **Admin** → **Export container** → the published version → **Export** | — |
| Create a SERVER container | Account → **Create container** → name → target platform **Server** | — |
| Container config (SERVER) | SERVER container → **Admin** → **Container settings** → **Manually provision tagging server** → copy **Container config** | [video](https://quanti-docs-assets.s3.fr-par.scw.cloud/sgtm/gtm-container-config-20260917.mp4) |
| Server container URLs (SERVER) | SERVER container → **Admin** → **Container settings** → *Server container URLs* → **Add URL** | — |
| GA4 client (SERVER) | SERVER container → **Clients** → *GA4* → **Migrate from JavaScript Managed Client ID** | — |
| Import a tag template (SERVER) | SERVER container → **Templates** → *Tag Templates* → **New** → **⋮** → **Import** | — |
| `server_container_url` (WEB) | WEB container → **Tags** → the Google tag (`G-…`) → **Configuration settings** → parameter `server_container_url` | — |
| Preview | Container → **Preview** (top right) — always from Tag Manager, never an old link | — |
| Publish | Container → **Submit** → version name → **Publish** | — |
| Publish a previous version (rollback) | Container → **Versions** → the version before → **⋯** → **Publish** | — |

## GA4

| What | Path |
|---|---|
| Create the test property | **Admin** → **Create** → **Property** → then a **Web** data stream; note the `G-` ID |
| Real-time / DebugView | **Reports** → **Realtime**; **Admin** → **DebugView** |

## The site's page source

`view-source:` in front of the site address, select all, save as a text file to attach.

## Network tab

Right click → **Inspect** → **Network** → reload → filter on the domain. Status 200 expected.
To test the snippet in one browser only: right click on `gtm.js` → **Block request URL** →
reload → **Console** → paste the first block without `<script>` tags → Enter. Remove the
rule after: ⋮ → **More tools** → **Network request blocking**.

## Quanti

| What | Where |
|---|---|
| Server-side servers | Quanti app → the project → **Server-side tagging** |
| Public guide | https://docs.quanti.io/server-side-tagging/setup-guide |
