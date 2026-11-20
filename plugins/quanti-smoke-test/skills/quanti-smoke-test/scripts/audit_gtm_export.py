"""Summarise a Google Tag Manager container export (JSON).

Smoke-test version of the future audit script: standard library only, prints one JSON
object on stdout. Usage: python3 audit_gtm_export.py <export.json>
"""
import json
import sys
from collections import Counter

TAG_LABELS = {
    "googtag": "Google tag",
    "gaawc": "GA4 configuration (legacy)",
    "gaawe": "GA4 event",
    "awct": "Google Ads conversion",
    "sp": "Google Ads remarketing",
    "flc": "Floodlight counter",
    "fls": "Floodlight sales",
    "html": "Custom HTML",
    "img": "Custom image",
}


def param(tag, key):
    for p in tag.get("parameter", []):
        if p.get("key") == key:
            return p.get("value")
    return None


def html_vendor(tag):
    code = param(tag, "html") or ""
    if "fbq(" in code:
        return "Meta pixel (custom HTML)"
    if "ttq." in code:
        return "TikTok pixel (custom HTML)"
    return None


def summarise(export):
    version = export.get("containerVersion", {})
    container = version.get("container", {})
    tags = version.get("tag", [])

    by_type = Counter()
    vendors = Counter()
    server_url = None
    for tag in tags:
        kind = tag.get("type", "unknown")
        label = TAG_LABELS.get(kind, "Community template" if kind.startswith("cvt_") else kind)
        by_type[label] += 1
        if kind == "html" and html_vendor(tag):
            vendors[html_vendor(tag)] += 1
        if kind in ("googtag", "gaawc"):
            server_url = server_url or param(tag, "server_container_url")

    return {
        "ok": True,
        "container_id": container.get("publicId"),
        "usage_context": container.get("usageContext"),
        "tags_total": len(tags),
        "tags_by_type": dict(by_type),
        "client_side_pixels": dict(vendors),
        "triggers_total": len(version.get("trigger", [])),
        "variables_total": len(version.get("variable", [])),
        "already_sends_to_server_container": server_url,
    }


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: audit_gtm_export.py <export.json>"}))
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            export = json.load(f)
        print(json.dumps(summarise(export), indent=2, ensure_ascii=False))
    except (OSError, ValueError) as err:
        print(json.dumps({"ok": False, "error": str(err)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
