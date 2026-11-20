"""Tests of the bundled scripts, on anonymised fixtures shaped like real exports.

Run: python3 tests/test_scripts.py -v
"""
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins/quanti-sgtm-server-to-server/skills/quanti-sgtm-server-to-server/scripts"
FIXTURES = ROOT / "tests/fixtures"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load("audit_gtm_export")
snippet = load("check_snippet")


def export(name):
    return json.loads((FIXTURES / name).read_text())


class AuditWebExport(unittest.TestCase):
    def setUp(self):
        self.out = audit.summarise(export("web-export.json"))

    def test_kind(self):
        self.assertEqual(self.out["kind"], "web")

    def test_server_url_read_through_google_tag_settings_variable(self):
        # Real exports put server_container_url in a "Google tag settings" variable (gtcs),
        # referenced by the tag, itself pointing at a constant variable.
        self.assertEqual(self.out["server_container_urls"], ["https://gtm.example.com"])
        routes = {r["tag"]: r for r in self.out["google_tags_routing"]}
        self.assertEqual(routes["Google Analytics G-ABC123"]["tag_id"], "G-ABC123")
        self.assertEqual(routes["Google Analytics G-ABC123"]["server_container_url"], ["https://gtm.example.com"])

    def test_client_side_pixels_and_ads(self):
        self.assertEqual(self.out["client_side_pixels"], {"Meta pixel": 1})
        self.assertEqual(self.out["google_ads_tags_in_browser"], ["Ads - purchase"])
        self.assertEqual(self.out["paused_tags"], ["Meta pixel"])

    def test_web_template_calling_provider_cdn(self):
        dep = self.out["provider_dependencies"]
        self.assertEqual([d["template"] for d in dep], ["Data Tag"])
        self.assertEqual(dep[0]["depends_on_provider"], ["Stape"])
        self.assertEqual(dep[0]["used_by"], 0)
        self.assertNotIn("developer.mozilla.org", dep[0]["calls_hosts"])


class AuditServerExport(unittest.TestCase):
    def setUp(self):
        self.out = audit.summarise(export("server-export.json"))

    def test_kind_urls_and_clients(self):
        self.assertEqual(self.out["kind"], "server")
        self.assertEqual(self.out["server_container_urls_setting"], ["https://gtm.example.com"])
        clients = {c["name"]: c for c in self.out["clients"]}
        self.assertEqual(clients["GA4"]["settings"]["cookieManagement"], "server")
        self.assertEqual(clients["GTM-WEB1234"]["custom_paths"],
                         [{"container_id": "GTM-WEB1234", "path": "/aB3xYz9"}])
        self.assertEqual(clients["Data Client - provider"]["type"], "Template: Data Client")

    def test_only_provider_hosts_are_dependencies(self):
        # Published by stape-io but calling HubSpot only: not a dependency on the host.
        templates = {t["template"]: t for t in self.out["custom_templates"]}
        self.assertEqual(templates["HubSpot"]["published_by"], "stape-io")
        self.assertEqual(templates["HubSpot"]["depends_on_provider"], [])
        self.assertEqual(templates["Data Client"]["published_by"], "Stape")
        self.assertEqual([d["template"] for d in self.out["provider_dependencies"]],
                         ["Store lookup (provider store)"])
        self.assertEqual(templates["HubSpot"]["used_by"], 1)

    def test_active_and_paused(self):
        self.assertEqual(self.out["active_tags"], ["GA4 - page_view"])
        self.assertEqual(self.out["paused_tags"], ["HubSpot page views"])

    def test_secrets_never_printed(self):
        self.assertNotIn("SECRET-TOKEN", json.dumps(self.out))


class CheckSnippet(unittest.TestCase):
    def test_custom_loader_from_host(self):
        out = snippet.analyse((FIXTURES / "snippet-custom-loader.html").read_text())
        self.assertTrue(out["uses_custom_path_from_host"])
        self.assertEqual(out["hosts"], ["gtm.example.com"])  # the CDN script is not a loader
        self.assertEqual(out["loaders"][0]["provider_hints"], ["Stape-style loader (?st=)"])

    def test_custom_path_declared_by_server_container(self):
        paths = snippet.server_paths(FIXTURES / "server-export.json")
        out = snippet.analyse((FIXTURES / "snippet-container-path.html").read_text(), paths)
        self.assertEqual(out["loaders"][0]["kind"], "served_by_server_container")
        self.assertFalse(out["uses_custom_path_from_host"])

    def test_same_path_without_server_export_is_flagged(self):
        out = snippet.analyse((FIXTURES / "snippet-container-path.html").read_text())
        self.assertEqual(out["loaders"][0]["kind"], "first_party_custom_path")

    def test_google_default(self):
        out = snippet.analyse((FIXTURES / "snippet-google-default.html").read_text())
        self.assertFalse(out["uses_custom_path_from_host"])
        self.assertEqual(out["loaders"][0]["kind"], "google_default")
        self.assertEqual(out["container_ids_in_page"], ["GTM-WEB1234"])

    def test_nothing_found(self):
        out = snippet.analyse("<html><script src='https://cdn.example.com/a.js'></script></html>")
        self.assertEqual(out["loaders"], [])
        self.assertIsNotNone(out["note"])


if __name__ == "__main__":
    unittest.main()
