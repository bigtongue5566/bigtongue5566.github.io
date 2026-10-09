"""Exercise catalog expansion and common publishing mistakes without dependencies."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("catalog_validator", ROOT / "scripts/validate_catalog.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class CatalogMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "docs/data/catalog.json").read_text(encoding="utf-8"))

    def check(self, data):
        return VALIDATOR.validate(data, ROOT / "docs")

    def test_published_catalog(self):
        self.assertEqual(self.check(self.catalog), [])

    def test_skill_with_new_category_and_no_demo(self):
        skill = copy.deepcopy(self.catalog["skills"][0])
        skill.update(id="example-tool", name="測試工具", category="新分類", demoIds=[])
        self.catalog["skills"].append(skill)
        self.assertEqual(self.check(self.catalog), [])

    def test_one_work_can_credit_several_skills(self):
        skill = copy.deepcopy(self.catalog["skills"][0])
        skill.update(id="example-collaborator", name="測試協作工具")
        self.catalog["skills"].append(skill)
        self.catalog["demos"][0]["contributors"].append({"skillId": skill["id"], "role": "測試協作"})
        self.assertEqual(self.check(self.catalog), [])

    def test_new_media_formats_need_no_video_fields(self):
        for kind in ["audio", "image", "interactive", "link"]:
            with self.subTest(media=kind):
                data = copy.deepcopy(self.catalog)
                demo = {"id": "example-" + kind, "title": "Test work", "summary": "A catalog fixture",
                        "description": "Tests a future media format.", "type": kind,
                        "src": "https://example.org/media", "contributors": [], "facts": []}
                data["demos"].append(demo)
                self.assertEqual(self.check(data), [])

    def test_broken_references_block_publication(self):
        data = copy.deepcopy(self.catalog)
        data["skills"][0]["demoIds"] = ["missing-work"]
        self.assertTrue(any("unknown demo reference" in error for error in self.check(data)))
        data = copy.deepcopy(self.catalog)
        data["demos"][0]["contributors"][0]["skillId"] = "missing-skill"
        self.assertTrue(any("unknown contributing skill" in error for error in self.check(data)))

    def test_invalid_resource_and_duplicate_id_block_publication(self):
        for value in ["javascript:alert(1)", "http://example.org/media", "https://user:password@example.org/media", "../README.md"]:
            with self.subTest(resource=value):
                data = copy.deepcopy(self.catalog)
                data["demos"][0]["src"] = value
                self.assertTrue(self.check(data))
        self.catalog["skills"].append(copy.deepcopy(self.catalog["skills"][0]))
        self.assertTrue(any("duplicate id" in error for error in self.check(self.catalog)))

    def test_companion_links_point_to_other_published_works(self):
        demo = self.catalog["demos"][0]
        demo["relatedDemoId"] = "missing-soundtrack"
        self.assertTrue(any("related demo reference" in error for error in self.check(self.catalog)))
        demo["relatedDemoId"] = demo["id"]
        self.assertTrue(any("related demo reference" in error for error in self.check(self.catalog)))

    def test_sourced_demo_claims_require_valid_citations(self):
        demo = self.catalog["demos"][0]
        demo["references"] = [{"id":"S1", "title":"Company profile", "publisher":"Company", "scope":"Founding year", "checkedDate":"2026-10-10", "url":"https://example.org/profile"}]
        demo["claims"] = [{"time":"00:08–00:20", "text":"Founded in a stated year", "sourceIds":["S1"]}]
        self.assertEqual(self.check(self.catalog), [])
        demo["claims"][0]["sourceIds"] = ["S9"]
        self.assertTrue(any("claim must cite" in error for error in self.check(self.catalog)))
        demo["claims"][0]["sourceIds"] = ["S1"]
        demo["references"][0]["url"] = "javascript:alert(1)"
        self.assertTrue(self.check(self.catalog))


if __name__ == "__main__":
    unittest.main()
