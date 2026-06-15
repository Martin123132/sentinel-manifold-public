import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-suite.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_suite", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SuiteValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator_module()

    def test_templates_validate_and_run(self):
        template_paths = sorted((ROOT / "samples" / "templates").glob("*.json"))

        self.assertEqual(len(template_paths), 5)
        for template_path in template_paths:
            with self.subTest(template=template_path.name):
                self.assertEqual(self.validator.validate_suite_file(template_path, run=True), [])

    def test_invalid_policy_profile_is_rejected(self):
        payload = {
            "policy_profile": "unknown",
            "cases": [
                {
                    "id": "bad-profile",
                    "references": ["Earth orbits the Sun."],
                    "candidates": [{"id": "safe", "text": "Earth orbits the Sun."}],
                    "expect": {"action": "EMIT"},
                }
            ],
        }

        errors = self.validator.validate_suite_payload(payload, source="test")

        self.assertTrue(any("policy_profile must be one of" in error for error in errors))

    def test_missing_required_case_shape_is_rejected(self):
        payload = {
            "cases": [
                {
                    "id": "",
                    "candidates": [{"id": "candidate-a", "text": ""}],
                    "expect": {"action": "ALLOW"},
                }
            ]
        }

        errors = self.validator.validate_suite_payload(payload, source="test")

        self.assertIn("test: cases[0].id must be a non-empty string", errors)
        self.assertIn("test: cases[0].references must be a non-empty string or list of strings", errors)
        self.assertIn("test: cases[0].candidates[0].text must be a non-empty string", errors)
        self.assertIn("test: cases[0].expect.action must be EMIT or BLOCK", errors)

    def test_existing_integration_suite_validates_and_runs(self):
        path = ROOT / "samples" / "integration-starter-suite.json"

        self.assertEqual(self.validator.validate_suite_file(path, run=True), [])

    def test_expand_suite_paths_handles_globs(self):
        paths = self.validator.expand_suite_paths([str(ROOT / "samples" / "templates" / "*.json")])

        self.assertEqual(len(paths), 5)


if __name__ == "__main__":
    unittest.main()
