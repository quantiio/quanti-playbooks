"""Audit a Google Tag Manager container export (JSON), web or server.

Standard library only. Prints one JSON object on stdout.
Usage: python3 audit_gtm_export.py <export.json>

What it answers, for a migration between server-side hosts:
- WEB container: which Google tags send to a server container, and at which URL
  (server_container_url), which pixels still run in the browser, which Google Ads tags
  stay client-side.
- SERVER container: its clients and tags, and the custom templates that come from a
  hosting provider's gallery (they may depend on a feature of that provider).

It reads the export only. It never prints parameter values other than URLs and IDs:
an export can contain API tokens (Meta CAPI, etc.).
"""
import json
import re
import sys
from collections import Counter

TAG_LABELS = {
    "googtag": "Google tag",
    "gaawc": "GA4 configuration (legacy)",
    "gaawe": "GA4 event",
    "awct": "Google Ads conversion",
    "sp": "Google Ads remarketing",
    "gclidw": "Conversion linker",
    "flc": "Floodlight counter",
    "fls": "Floodlight sales",
    "html": "Custom HTML",
    "img": "Custom image",
    "sgtmgaaw": "GA4 (server)",
    "sgtmadsct": "Google Ads conversion (server)",
    "sgtmadsrm": "Google Ads remarketing (server)",
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

# Gallery owners and names that belong to a hosting provider rather than to a vendor.
PROVIDER_HINTS = ["stape", "addingwell", "taggrs", "jentis", "tagstack"]

SERVER_URL_NAME = re.compile(r"server_?container_?url", re.IGNORECASE)
VARIABLE_REF = re.compile(r"\{\{([^}]+)\}\}")


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
    def sub(m):
        return constants.get(m.group(1), m.group(0))
    return VARIABLE_REF.sub(sub, value)
# #endregion


# #region provider_hint
def provider_hint(*texts):
    blob = " ".join(t for t in texts if t).lower()
    return next((h for h in PROVIDER_HINTS if h in blob), None)
# #endregion


# #region audit_web
def audit_web(version, constants):
    tags = version.get("tag", [])
    by_type, pixels, routes, ads_client_side = Counter(), Counter(), [], []
    for tag in tags:
        kind = tag.get("type", "unknown")
        by_type[TAG_LABELS.get(kind, "Community template" if kind.startswith("cvt_") else kind)] += 1
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
        if kind in ("googtag", "gaawc", "gaawe") or found:
            routes.append({
                "tag": tag.get("name"),
                "type": TAG_LABELS.get(kind, kind),
                "tag_id": param(tag, "tagId") or param(tag, "measurementId") or param(tag, "measurementIdOverride"),
                "server_container_url": [resolve(u, constants) for u in found] or None,
                "paused": bool(tag.get("paused")),
            })
    urls = sorted({u for r in routes for u in (r["server_container_url"] or [])})
    return {
        "tags_total": len(tags),
        "tags_by_type": dict(by_type),
        "google_tags_routing": routes,
        "server_container_urls": urls,
        "client_side_pixels": dict(pixels),
        "google_ads_tags_in_browser": ads_client_side,
    }
# #endregion


# #region audit_server
def audit_server(version):
    templates = {}
    flagged = []
    for t in version.get("customTemplate", []):
        ref = t.get("galleryReference") or {}
        owner, repo = ref.get("owner"), ref.get("repository")
        templates[t.get("templateId")] = t.get("name")
        hint = provider_hint(t.get("name"), owner, repo)
        if hint:
            flagged.append({"template": t.get("name"), "gallery_owner": owner, "repository": repo, "provider": hint})

    def label(kind):
        if kind.startswith("cvt_"):
            return "Template: " + str(templates.get(kind.split("_")[-1], kind))
        return TAG_LABELS.get(kind, kind)

    clients = [{"name": c.get("name"), "type": label(c.get("type", "")),
                "settings": sorted(p.get("key") for p in c.get("parameter", []))}
               for c in version.get("client", [])]
    tags = version.get("tag", [])
    by_type = Counter(label(t.get("type", "unknown")) for t in tags)
    variables = [v.get("name") for v in version.get("variable", [])
                 if provider_hint(v.get("name"), v.get("type"))]
    for name in variables:
        flagged.append({"variable": name, "provider": provider_hint(name)})
    return {
        "clients": clients,
        "tags_total": len(tags),
        "tags_by_type": dict(by_type),
        "paused_tags": [t.get("name") for t in tags if t.get("paused")],
        "provider_specific": flagged,
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
    out.update(audit_server(version) if out["kind"] == "server" else audit_web(version, constants))
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
    except (OSError, ValueError, AttributeError) as err:
        print(json.dumps({"ok": False, "error": f"{type(err).__name__}: {err}"}))
        sys.exit(1)
# #endregion


if __name__ == "__main__":
    main()
