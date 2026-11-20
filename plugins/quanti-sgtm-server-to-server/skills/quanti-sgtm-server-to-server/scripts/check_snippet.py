"""Find where a website loads Google Tag Manager from, in its HTML or a pasted snippet.

Standard library only. Prints one JSON object on stdout.
Usage: python3 check_snippet.py <file.html|snippet.txt>

For each loader found: the host, the path, whether it is Google's default address, a
first-party host on GTM's standard path, or a first-party host on a custom path (a
hosting provider's "custom loader"). That last case matters for a migration: the new
host does not serve the old provider's custom paths.
"""
import json
import re
import sys
from urllib.parse import urlsplit, parse_qs

# j.src='https://host/path?x='+i+dl  |  <script src="https://host/path?...">  |  <iframe src="...">
SRC = re.compile(r"""(\.src\s*=|src\s*=)\s*['"](https?://[^'"\s]+)""", re.IGNORECASE)
CONTAINER = re.compile(r"GTM-[A-Z0-9]{4,10}")
GOOGLE_HOSTS = ("www.googletagmanager.com", "googletagmanager.com")
# Query parameter names that public filter lists attribute to a provider's loader.
PARAM_HINTS = {"st": "Stape-style loader (?st=)", "aw": "Addingwell-style loader (?aw=)"}


# #region classify
def classify(url):
    parts = urlsplit(url)
    host, path = parts.hostname or "", parts.path or "/"
    query = parse_qs(parts.query, keep_blank_values=True)
    if host in GOOGLE_HOSTS:
        kind = "google_default"
    elif path.rstrip("/").endswith(("/gtm.js", "/ns.html")):
        kind = "first_party_standard_path"
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
def analyse(text):
    loaders = []
    for m in SRC.finditer(text):
        url = m.group(2)
        before = text[max(0, m.start() - 400): m.start()]
        if looks_like_gtm(url, m.group(1).startswith("."), before):
            loaders.append(classify(url))
    seen, unique = set(), []
    for l in loaders:
        key = (l["host"], l["path"])
        if key not in seen:
            seen.add(key)
            unique.append(l)
    kinds = {l["kind"] for l in unique}
    return {
        "ok": True,
        "loaders": unique,
        "container_ids_in_page": sorted(set(CONTAINER.findall(text))),
        "uses_custom_path": "first_party_custom_path" in kinds,
        "hosts": sorted({l["host"] for l in unique}),
        "note": None if unique else "No GTM loader found: the snippet may be injected by a CMS plugin or a tag manager extension. Ask for the page source (view-source:) of the home page.",
    }
# #endregion


# #region main
def main():
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: check_snippet.py <file>"}))
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
            print(json.dumps(analyse(f.read()), indent=2, ensure_ascii=False))
    except OSError as err:
        print(json.dumps({"ok": False, "error": str(err)}))
        sys.exit(1)
# #endregion


if __name__ == "__main__":
    main()
