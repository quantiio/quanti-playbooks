"""Audit a Google Tag Manager container export (JSON), web or server.

Standard library only. Prints one JSON object on stdout.
Usage: python3 audit_gtm_export.py <export.json>

What it answers, for a migration between server-side hosts:
- WEB container: which Google tags send to a server container and at which URL
  (server_container_url, set on the tag or in a "Google tag settings" variable), which
  pixels still run in the browser, which Google Ads tags stay client-side.
- SERVER container: its server container URLs, its clients (with the custom paths of the
  GTM client), its tags, and the custom templates that call a hosting provider's domain.
- Both: custom templates, whether a tag uses them, and the external hosts they call.

It reads the export only. It prints names, types, IDs and URLs, never other parameter
values: an export can contain API tokens (Meta CAPI, HubSpot, etc.).
"""
import json
import re
import sys
from collections import Counter

TAG_LABELS = {
    "googtag": "Google tag",
    "gaawc": "GA4 configuration (legacy)",
    "gaawe": "GA4 event",
    "dest_ga": "Google Analytics destination",
    "awct": "Google Ads conversion",
    "sp": "Google Ads remarketing",
    "gclidw": "Conversion linker",
    "flc": "Floodlight counter",
    "fls": "Floodlight sales",
    "html": "Custom HTML",
    "img": "Custom image",
    "http_request": "HTTP request",
    "sgtmgaaw": "GA4 (server)",
    "sgtmadsct": "Google Ads conversion (server)",
    "sgtmadsrm": "Google Ads remarketing (server)",
    "gaaw_client": "GA4 client",
    "ua_client": "Universal Analytics client",
    "gtm_client": "Google Tag Manager web container client",
}

HTML_VENDORS = [
    ("fbq(", "Meta pixel"),
    ("ttq.", "TikTok pixel"),
    ("pintrk(", "Pinterest tag"),
    ("snaptr(", "Snap pixel"),
    ("lintrk(", "LinkedIn Insight"),
    ("_linkedin_partner_id", "LinkedIn Insight"),
    ("criteo_q", "Criteo OneTag"),
    ("uetq", "Microsoft Ads UET"),
]

# Domains that belong to a server-side hosting provider. A template that calls one of them
# depends on that provider, whoever published it.
PROVIDER_DOMAINS = {"stape.io": "Stape", "stapecdn.com": "Stape", "stape.net": "Stape",
                    "addingwell.com": "Addingwell", "taggrs.io": "TAGGRS"}
# Client settings that are safe to print (no secret) and matter for a migration.
CLIENT_SETTINGS = {"cookieManagement", "cookieName", "cookieDomain", "migrateFromJsClientId",
                   "activateDefaultPaths"}

SERVER_URL_NAME = re.compile(r"server_?container_?url", re.IGNORECASE)
VARIABLE_REF = re.compile(r"\{\{([^}]+)\}\}")
URL_HOST = re.compile(r"https?://([a-z0-9.-]+\.[a-z]{2,})", re.IGNORECASE)
# Hosts present in almost every template (docs, gallery, Google itself): not a dependency.
IGNORED_HOSTS = ("developers.google.com", "support.google.com", "github.com", "www.simoahava.com",
                 "developer.mozilla.org", "tagmanager.google.com")


# #region walk_params
def walk_params(params, found):
    """Collect every server container URL set anywhere in a parameter tree."""
    for p in params or []:
        key = p.get("key", "")
        if SERVER_URL_NAME.search(key) and isinstance(p.get("value"), str):
            found.append(p["value"])
        if p.get("type") == "MAP":
            entries = {m.get("key"): m.get("value") for m in p.get("map", [])}
            name = entries.get("parameter") or entries.get("name") or ""
            if isinstance(name, str) and SERVER_URL_NAME.search(name):
                value = entries.get("parameterValue") or entries.get("value")
                if isinstance(value, str):
                    found.append(value)
            walk_params(p.get("map"), found)
        if p.get("type") == "LIST":
            walk_params(p.get("list"), found)
# #endregion


# #region param
def param(item, key):
    for p in item.get("parameter", []):
        if p.get("key") == key:
            return p.get("value")
    return None
# #endregion


# #region resolve
def resolve(value, constants):
    """Replace {{Variable}} by its value when the variable is a constant."""
    return VARIABLE_REF.sub(lambda m: constants.get(m.group(1), m.group(0)), value)
# #endregion


# #region provider_of
def provider_of(host):
    host = host.lower()
    return next((name for dom, name in PROVIDER_DOMAINS.items()
                 if host == dom or host.endswith("." + dom)), None)
# #endregion


# #region audit_templates
def audit_templates(version):
    """Custom templates: who published them, whether a tag/client/variable uses them, and
    the external hosts their code calls (provider hosts flagged)."""
    used = Counter()
    for kind in ("tag", "client", "variable"):
        for item in version.get(kind, []):
            t = item.get("type", "")
            if t.startswith("cvt_"):
                used[t.split("_")[-1]] += 1
    out = []
    for t in version.get("customTemplate", []):
        ref = t.get("galleryReference") or {}
        body = t.get("templateData", "")
        hosts = sorted({h.lower() for h in URL_HOST.findall(body)
                        if not any(h.lower().endswith(i) for i in IGNORED_HOSTS)})
        brand = re.search(r'"displayName":\s*"([^"]*)"', body.split('"brand"', 1)[1]) if '"brand"' in body else None
        providers = sorted({p for p in (provider_of(h) for h in hosts) if p})
        out.append({
            "template": t.get("name"),
            "published_by": ref.get("owner") or (brand.group(1) if brand else None) or "custom (not from the gallery)",
            "used_by": used.get(str(t.get("templateId")), 0),
            "calls_hosts": hosts,
            "depends_on_provider": providers,
        })
    return out
# #endregion


# #region template_names
def template_names(version):
    return {str(t.get("templateId")): t.get("name") for t in version.get("customTemplate", [])}
# #endregion


# #region label
def label(kind, templates):
    if kind.startswith("cvt_"):
        return "Template: " + str(templates.get(kind.split("_")[-1], kind))
    return TAG_LABELS.get(kind, kind)
# #endregion


# #region audit_web
def audit_web(version, constants):
    templates = template_names(version)
    # "Google tag settings" variables (gtcs): the server URL often lives here, not on the tag.
    settings_urls = {}
    for v in version.get("variable", []):
        found = []
        walk_params(v.get("parameter"), found)
        if found:
            settings_urls[v.get("name")] = [resolve(u, constants) for u in found]

    tags = version.get("tag", [])
    by_type, pixels, routes, ads_client_side = Counter(), Counter(), [], []
    for tag in tags:
        kind = tag.get("type", "unknown")
        by_type[label(kind, templates)] += 1
        if kind == "html":
            code = param(tag, "html") or ""
            for marker, vendor in HTML_VENDORS:
                if marker in code:
                    pixels[vendor] += 1
                    break
        if kind in ("awct", "sp", "flc", "fls"):
            ads_client_side.append(tag.get("name"))
        found = []
        walk_params(tag.get("parameter"), found)
        urls = [resolve(u, constants) for u in found]
        for key in ("configSettingsVariable", "eventSettingsVariable"):
            ref = param(tag, key)
            if isinstance(ref, str):
                for name in VARIABLE_REF.findall(ref):
                    urls += settings_urls.get(name, [])
        if kind in ("googtag", "gaawc", "gaawe", "dest_ga") or urls:
            routes.append({
                "tag": tag.get("name"),
                "type": label(kind, templates),
                "tag_id": param(tag, "tagId") or param(tag, "destinationId")
                or param(tag, "measurementId") or param(tag, "measurementIdOverride"),
                "server_container_url": sorted(set(urls)) or None,
                "paused": bool(tag.get("paused")),
            })
    return {
        "tags_total": len(tags),
        "tags_by_type": dict(by_type),
        "paused_tags": [t.get("name") for t in tags if t.get("paused")],
        "google_tags_routing": routes,
        "server_container_urls": sorted({u for r in routes for u in (r["server_container_url"] or [])}),
        "client_side_pixels": dict(pixels),
        "google_ads_tags_in_browser": ads_client_side,
    }
# #endregion


# #region gtm_client_paths
def gtm_client_paths(client):
    """Custom paths a GTM client serves web containers on (allowedContainerIds)."""
    out = []
    for p in client.get("parameter", []):
        if p.get("key") == "allowedContainerIds":
            for item in p.get("list", []):
                entries = {m.get("key"): m.get("value") for m in item.get("map", [])}
                out.append({"container_id": entries.get("containerId"), "path": entries.get("path")})
    return out
# #endregion


# #region audit_server
def audit_server(version, container):
    templates = template_names(version)
    clients = []
    for c in version.get("client", []):
        entry = {"name": c.get("name"), "type": label(c.get("type", ""), templates)}
        settings = {p.get("key"): p.get("value") for p in c.get("parameter", [])
                    if p.get("key") in CLIENT_SETTINGS}
        if settings:
            entry["settings"] = settings
        if c.get("type") == "gtm_client":
            entry["custom_paths"] = gtm_client_paths(c)
        clients.append(entry)
    tags = version.get("tag", [])
    return {
        "server_container_urls_setting": container.get("taggingServerUrls", []),
        "clients": clients,
        "tags_total": len(tags),
        "tags_by_type": dict(Counter(label(t.get("type", "unknown"), templates) for t in tags)),
        "active_tags": [t.get("name") for t in tags if not t.get("paused")],
        "paused_tags": [t.get("name") for t in tags if t.get("paused")],
    }
# #endregion


# #region summarise
def summarise(export):
    version = export.get("containerVersion", {})
    container = version.get("container", {})
    context = [c.upper() for c in container.get("usageContext", [])]
    constants = {v.get("name"): param(v, "value") for v in version.get("variable", [])
                 if v.get("type") == "c" and isinstance(param(v, "value"), str)}
    out = {
        "ok": True,
        "container_id": container.get("publicId"),
        "container_name": container.get("name"),
        "kind": "server" if "SERVER" in context else "web" if "WEB" in context else ",".join(context) or "unknown",
        "version": version.get("name") or version.get("containerVersionId"),
        "triggers_total": len(version.get("trigger", [])),
        "variables_total": len(version.get("variable", [])),
    }
    out.update(audit_server(version, container) if out["kind"] == "server" else audit_web(version, constants))
    templates = audit_templates(version)
    out["custom_templates"] = templates
    out["provider_dependencies"] = [t for t in templates if t["depends_on_provider"]]
    return out
# #endregion


# #region main
def main():
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: audit_gtm_export.py <export.json>"}))
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            export = json.load(f)
        print(json.dumps(summarise(export), indent=2, ensure_ascii=False))
    except (OSError, ValueError, AttributeError, IndexError) as err:
        print(json.dumps({"ok": False, "error": f"{type(err).__name__}: {err}"}))
        sys.exit(1)
# #endregion


if __name__ == "__main__":
    main()
