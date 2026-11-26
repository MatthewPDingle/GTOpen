#!/usr/bin/env python3
"""Three-player jobs in the uploader and the validator (no network, no solver).

    python -m pytest tools/datagen/test_three_player.py
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upload    # noqa: E402
import validate  # noqa: E402


def job_file(folder, name, records):
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return path


THREE_EXAMPLE = {"type": "example", "job": 5, "index": 0, "pot_type": "srp", "range": [[1], [1], [1]],
                 "tree_bytes": 7_000_000_000}
TWO_EXAMPLE = {"type": "example", "job": 5, "index": 0, "pot_type": "srp", "range": [[1], [1]],
               "tree_bytes": 2_000_000_000}


class ThreePlayerTests(unittest.TestCase):
    def test_the_uploader_sends_each_kind_of_job_to_its_folder(self):
        with tempfile.TemporaryDirectory() as out:
            d = os.path.join(out, "alice")
            os.makedirs(d)
            two = job_file(d, "job-12.jsonl", [{"type": "header", "contributor": "alice", "examples": 1}])
            three = job_file(d, "job3-34.jsonl", [{"type": "header", "contributor": "alice", "examples": 1}])
            job_file(d, "job3-56.jsonl.part", [])
            self.assertEqual(sorted(upload.finished_jobs(out, "alice")), sorted([two, three]))
            self.assertEqual(upload.repo_path(two, "alice"), "data/alice/job-12.jsonl.gz")
            self.assertEqual(upload.repo_path(three, "alice"), "three/alice/job-34.jsonl.gz")
            open(three + ".uploaded", "w").close()
            self.assertEqual(upload.finished_jobs(out, "alice"), [two])

    def test_the_validator_knows_both_folders(self):
        self.assertEqual(validate.job_match("data/alice/job-12.jsonl.gz").groups(), ("alice", "12"))
        self.assertEqual(validate.job_match("three/alice/job-34.jsonl.gz").groups(), ("alice", "34"))
        self.assertIsNone(validate.job_match("three/alice/job3-34.jsonl.gz"))
        self.assertIsNone(validate.job_match("other/alice/job-34.jsonl.gz"))

    def test_three_player_solves_are_counted_under_their_own_name(self):
        with tempfile.TemporaryDirectory() as d:
            path = job_file(d, "job3-34.jsonl", [
                {"type": "header"}, THREE_EXAMPLE, dict(THREE_EXAMPLE, index=1, pot_type="3bet"),
                {"type": "skipped", "job": 5, "index": 2, "reason": "no draw fits this card"}, {"type": "done"}])
            self.assertEqual(validate.kinds_in(path), {
                "spots": {"three-player": 2}, "spot_types": {"three-player": {"srp": 1, "3bet": 1}},
                "sizes": {"6-12": 2}})
            path = job_file(d, "job-12.jsonl", [{"type": "header"}, TWO_EXAMPLE, {"type": "done"}])
            self.assertEqual(validate.kinds_in(path), {"spots": {}, "spot_types": {}, "sizes": {"0-6": 1}})

    def test_a_job_in_the_wrong_folder_is_refused(self):
        base = {"contributor": "alice", "job": 7, "examples": 1, "errors": []}
        with mock.patch.object(validate, "block_base", return_value=0):
            for players, three, ok in [(3, True, True), (None, False, True), (3, False, False), (None, True, False)]:
                summary = dict(base, **({"players": players} if players else {}))
                with mock.patch.object(validate, "verify_file", return_value=summary):
                    errors, _ = validate.check_job("solve-cli", "alice", 7, "f.jsonl", 1, three=three)
                self.assertEqual(not errors, ok, (players, three, errors))

    def test_the_stage_for_three_player_flops_draws_its_bar(self):
        import progress_chart
        cfg = progress_chart.load_config()
        stage = [s for s in cfg["stages"] if (s.get("target") or {}).get("list") == validate.THREE]
        self.assertEqual(len(stage), 1)
        progress = {"events": [{"date": "2026-11-27", "time": "2026-11-27T10:00:00+00:00", "contributor": "alice",
                                "jobs": 1, "examples": 9, "pr": 1, "spots": {validate.THREE: 9}, "spot_types": {}}]}
        svg = progress_chart.render_svg(progress, cfg)
        self.assertIn(f">9</tspan> of {stage[0]['target']['solves']:,} of these spots solved", svg)


if __name__ == "__main__":
    unittest.main()
