import unittest
from pathlib import Path


class PushReadinessTests(unittest.TestCase):
    def test_helper_scripts_prefer_repo_venv(self):
        for path in [Path("scripts/run_scraper.sh"), Path("scripts/view_data.sh"), Path("scripts/run_alerts.sh")]:
            content = path.read_text(encoding="utf-8")
            self.assertIn('.venv/bin/python', content)
            self.assertIn('python3', content)

    def test_runtime_outputs_are_gitignored(self):
        content = Path(".gitignore").read_text(encoding="utf-8")
        self.assertIn("news/", content)
        self.assertIn("state/", content)


if __name__ == "__main__":
    unittest.main()
