"""Find where a website loads Google Tag Manager from, in its HTML or a pasted snippet.

Standard library only. Prints one JSON object on stdout.
Usage: python3 check_snippet.py <page-source.html> [<server-container-export.json>]

For each loader found: the host, the path, and what serves it:
- google_default: www.googletagmanager.com, nothing to migrate on the page;
- first_party_standard_path: the site's own host on GTM's standard path (/gtm.js);
- served_by_server_container: a custom path declared in the GTM client of the server
  container (needs the server export). It moves with the container: any host serves it;
- first_party_custom_path: a custom path NOT declared in the server container. It comes
  from the current host's infrastructure (a "custom loader"), which the new host does not
  serve: the snippet must be replaced during the migration.
"""
import json
import re
import sys
from urllib.parse import urlsplit, parse_qs

SRC = re.compile(r"""(\.src\s*=|src\s*=)\s*['"](https?://[^'"\s]+)""", re.IGNORECASE)
CONTAINER = re.compile(r"GTM-[A-Z0-9]{4,10}")
GOOGLE_HOSTS = ("www.googletagmanager.com", "googletagmanager.com")
# Query parameter names that public filter lists attribute to a provider's loader.
PARAM_HINTS = {"st": "Stape-style loader (?st=)", "aw": "Addingwell-style loader (?aw=)"}


# #region server_paths
def server_paths(export_path):
    """Custom paths declared by the GTM client(s) of a server container export."""
    with open(export_path, encoding="utf-8") as f:
        version = json.load(f).get("containerVersion", {})
    paths = []
    for client in version.get("client", []):
        if client.get("type") != "gtm_client":
            continue
        for p in client.get("parameter", []):
            if p.get("key") != "allowedContainerIds":
                continue
            for item in p.get("list", []):
                entries = {m.get("key"): m.get("value") for m in item.get("map", [])}
                if entries.get("path"):
                    paths.append(entries["path"].rstrip("/"))
    return paths
# #endregion


# #region classify
def classify(url, declared_paths):
    parts = urlsplit(url)
    host, path = parts.hostname or "", parts.path or "/"
    query = parse_qs(parts.query, keep_blank_values=True)
    if host in GOOGLE_HOSTS:
        kind = "google_default"
    elif path.rstrip("/").endswith(("/gtm.js", "/ns.html")):
        kind = "first_party_standard_path"
    elif any(path == p or path.startswith(p + "/") for p in declared_paths):
        kind = "served_by_server_container"
    else:
        kind = "first_party_custom_path"
    hints = [label for key, label in PARAM_HINTS.items() if key in query]
    return {"url": url.split("'")[0], "host": host, "path": path, "kind": kind,
            "query_params": sorted(query), "provider_hints": hints}
# #endregion


# #region looks_like_gtm
def looks_like_gtm(url, js_assignment, text_before):
    """Keep GTM loaders and iframes, not every script of the page.

    A custom loader can have any path: it is recognised by being the `j.src=` of the
    GTM bootstrap code, which pushes 'gtm.start' just before.
    """
    u = url.lower()
    if "googletagmanager" in u or "gtm.js" in u or "ns.html" in u:
        return True
    return js_assignment and "gtm.start" in text_before
# #endregion


# #region analyse
def analyse(text, declared_paths=()):
    loaders = []
    for m in SRC.finditer(text):
        url = m.group(2)
        before = text[max(0, m.start() - 400): m.start()]
        if looks_like_gtm(url, m.group(1).startswith("."), before):
            loaders.append(classify(url, declared_paths))
    seen, unique = set(), []
    for loader in loaders:
        key = (loader["host"], loader["path"])
        if key not in seen:
            seen.add(key)
            unique.append(loader)
    kinds = {loader["kind"] for loader in unique}
    return {
        "ok": True,
        "loaders": unique,
        "container_ids_in_page": sorted(set(CONTAINER.findall(text))),
        "server_export_checked": bool(declared_paths),
        "uses_custom_path_from_host": "first_party_custom_path" in kinds,
        "hosts": sorted({loader["host"] for loader in unique}),
        "note": None if unique else "No GTM loader found: the snippet may be injected by a CMS plugin or a tag manager extension. Ask for the page source (view-source:) of the home page.",
    }
# #endregion


# #region main
def main():
    if len(sys.argv) not in (2, 3):
        print(json.dumps({"ok": False, "error": "usage: check_snippet.py <file> [<server-export.json>]"}))
        sys.exit(2)
    try:
        declared = server_paths(sys.argv[2]) if len(sys.argv) == 3 else []
        with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
            print(json.dumps(analyse(f.read(), declared), indent=2, ensure_ascii=False))
    except (OSError, ValueError) as err:
        print(json.dumps({"ok": False, "error": str(err)}))
        sys.exit(1)
# #endregion


if __name__ == "__main__":
    main()
