import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run-proof-pack.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("run_proof_pack", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProofPackRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner_module()

    def test_default_trial_pack_contains_expected_suites(self):
        inputs = {suite["input"] for suite in self.runner.DEFAULT_SUITES}

        self.assertEqual(
            inputs,
            {
                "samples/regression-suite.json",
                "samples/customer-shaped-regression-suite.json",
                "samples/policy-calibration-suite.json",
                "samples/integration-starter-suite.json",
                "samples/mixed-proof-suite.json",
            },
        )

    def test_full_pack_adds_extended_suites_without_duplicates(self):
        all_suites = self.runner.DEFAULT_SUITES + self.runner.FULL_SUITES
        inputs = [suite["input"] for suite in all_suites]

        self.assertEqual(len(inputs), len(set(inputs)))
        self.assertIn("samples/agent-policy-suite.json", inputs)
        self.assertIn("samples/buyer-policy-depth-suite.json", inputs)
        self.assertIn("samples/policy-tuning-suite.json", inputs)
        self.assertIn("examples/external-adoption/support-assistant/sentinel-suite.json", inputs)

    def test_runner_suite_files_exist(self):
        all_suites = self.runner.DEFAULT_SUITES + self.runner.FULL_SUITES

        for suite in all_suites:
            with self.subTest(suite=suite["name"]):
                self.assertTrue((ROOT / suite["input"]).exists())

    def test_display_path_handles_paths_outside_repo(self):
        outside_path = Path("C:/tmp/sentinel-out")

        self.assertEqual(self.runner.display_path(ROOT / "out", ROOT), "out")
        self.assertEqual(self.runner.display_path(outside_path, ROOT), str(outside_path))


if __name__ == "__main__":
    unittest.main()
