"""Tests of the bundled scripts, on fixtures shaped like real exports.

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


class AuditWebExport(unittest.TestCase):
    def setUp(self):
        self.out = audit.summarise(json.loads((FIXTURES / "web-export.json").read_text()))

    def test_kind(self):
        self.assertEqual(self.out["kind"], "web")

    def test_server_url_resolved_from_constant_variable(self):
        self.assertEqual(self.out["server_container_urls"], ["https://gtm.example.com"])

    def test_client_side_pixels_and_ads(self):
        self.assertEqual(self.out["client_side_pixels"], {"Meta pixel": 1})
        self.assertEqual(self.out["google_ads_tags_in_browser"], ["Ads - purchase"])


class AuditServerExport(unittest.TestCase):
    def setUp(self):
        self.out = audit.summarise(json.loads((FIXTURES / "server-export.json").read_text()))

    def test_kind_and_clients(self):
        self.assertEqual(self.out["kind"], "server")
        self.assertEqual([c["name"] for c in self.out["clients"]], ["GA4", "Custom loader"])

    def test_provider_specific_items_flagged(self):
        flagged = self.out["provider_specific"]
        self.assertIn("stape-io", [f.get("gallery_owner") for f in flagged])
        self.assertIn("Stape Store lookup", [f.get("variable") for f in flagged])
        self.assertNotIn("facebookincubator", [f.get("gallery_owner") for f in flagged])

    def test_secrets_never_printed(self):
        self.assertNotIn("SECRET-TOKEN", json.dumps(self.out))


class CheckSnippet(unittest.TestCase):
    def test_custom_loader(self):
        out = snippet.analyse((FIXTURES / "snippet-custom-loader.html").read_text())
        self.assertTrue(out["uses_custom_path"])
        self.assertEqual(out["hosts"], ["gtm.example.com"])  # the CDN script is not a loader
        self.assertEqual(out["loaders"][0]["provider_hints"], ["Stape-style loader (?st=)"])

    def test_google_default(self):
        out = snippet.analyse((FIXTURES / "snippet-google-default.html").read_text())
        self.assertFalse(out["uses_custom_path"])
        self.assertEqual(out["loaders"][0]["kind"], "google_default")
        self.assertEqual(out["container_ids_in_page"], ["GTM-WEB1234"])

    def test_nothing_found(self):
        out = snippet.analyse("<html><script src='https://cdn.example.com/a.js'></script></html>")
        self.assertEqual(out["loaders"], [])
        self.assertIsNotNone(out["note"])


if __name__ == "__main__":
    unittest.main()
