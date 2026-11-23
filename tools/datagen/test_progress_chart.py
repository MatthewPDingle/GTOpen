"""Tests for progress_chart.py: the graph of the pool's progress and the stages listed under it.

    python tools/datagen/test_progress_chart.py
"""
import datetime
import json
import os
import re
import sys
import unittest
from xml.dom import minidom

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import progress_chart  # noqa: E402

CFG = {"go_no_go_examples": 50, "goal_examples": 300}
STAGES = [{"since": "2026-11-06", "title": "Random ranges", "for": "Data for the first nets."},
          {"since": "2026-11-21T01:53:00+00:00", "title": "Half spots from our own solves <mix 2>",
           "for": "Data for the next net.", "target": {"list": "outside-hands-1", "solves": 1000}}]


NOW = datetime.datetime(2026, 11, 21, 12, tzinfo=datetime.timezone.utc)   # the graph's right edge in these tests
BY_TYPE = {"limped": 100, "srp": 300, "3bet": 300, "4bet": 300}


def render(p, cfg):
    return progress_chart.render_svg(p, cfg, now=NOW)


def progress(*events):
    return {"updated": "2026-11-22T00:00:00+00:00",
            "events": [dict({"date": t[:10], "time": t, "contributor": "Anyone", "jobs": 1}, **more) for t, more in events]}


def height(svg):
    return int(re.search(r'viewBox="0 0 820 (\d+)"', svg).group(1))


class ChartTests(unittest.TestCase):
    def test_without_stages_the_graph_is_as_it_was(self):
        svg = render(progress(("2026-11-07T10:00:00+00:00", {"examples": 100})), CFG)
        minidom.parseString(svg)
        self.assertEqual(height(svg), 340)
        self.assertNotIn("What the pool solves", svg)
        self.assertIn("33.3% of the 300 goal", svg)

    def test_stages_are_listed_with_what_they_are_for_and_the_target_bar_counts_the_lists_examples(self):
        p = progress(("2026-11-07T10:00:00+00:00", {"examples": 100}),
                     ("2026-11-21T05:00:00+00:00", {"examples": 80, "spots": {"outside-hands-1": 41}}),
                     ("2026-11-21T09:00:00+00:00", {"examples": 60, "spots": {"outside-hands-1": 29, "another": 5}}))
        svg = render(p, dict(CFG, stages=STAGES))
        minidom.parseString(svg)                              # the title's < is escaped
        self.assertEqual(height(svg), 340 + 34 + 2 * 42 + 24 + 8)
        for text in ("From Nov 6:", "Random ranges", "Data for the first nets.", "From Nov 21:",
                     "Half spots from our own solves &lt;mix 2&gt;", "Data for the next net.", "of 1,000 of these spots solved"):
            self.assertIn(text, svg)
        self.assertIn(">70</tspan>", svg)
        self.assertEqual(progress_chart.spots(p), {"outside-hands-1": 70, "another": 5})
        self.assertEqual(svg.count('class="stage"'), 1)       # the first stage began before the graph: no line, only its number
        self.assertNotIn("target reached", svg)

    def test_a_reached_target_and_a_passed_goal_say_so(self):
        p = progress(("2026-11-21T05:00:00+00:00", {"examples": 2400, "spots": {"outside-hands-1": 1200}}))
        svg = render(p, dict(CFG, stages=STAGES))
        self.assertIn("past the 300 goal", svg)
        self.assertIn("target reached", svg)

    def test_a_target_by_pot_type_counts_a_pot_type_only_up_to_what_it_needs(self):
        stages = [dict(STAGES[1], target=dict(STAGES[1]["target"], by_pot_type=BY_TYPE))]
        p = progress(("2026-11-21T05:00:00+00:00", {"examples": 900, "spots": {"outside-hands-1": 700},
                                                    "spot_types": {"outside-hands-1": {"srp": 120, "4bet": 380}}}),
                     ("2026-11-21T09:00:00+00:00", {"examples": 300, "spots": {"outside-hands-1": 200},
                                                    "spot_types": {"outside-hands-1": {"4bet": 150, "3bet": 50}}}))
        svg = render(p, dict(CFG, stages=stages))
        minidom.parseString(svg)
        self.assertEqual(progress_chart.spot_types(p), {"outside-hands-1": {"srp": 120, "4bet": 530, "3bet": 50}})
        # 900 examples came from the list, but 230 of them are 4-bet pots beyond the 300 the target needs
        self.assertIn(">470</tspan> of 1,000 of these spots solved", svg)
        for text in ("Limped pots", "0 of 100", "Single-raised pots", "120 of 300", "3-bet pots", "50 of 300",
                     "4-bet pots", "530 of 300 · enough"):
            self.assertIn(text, svg)
        self.assertEqual(height(svg), 340 + 34 + 42 + 24 + 4 * 17 + 6 + 8)
        self.assertNotIn("target reached", svg)

    def test_a_target_by_pot_type_falls_back_to_the_lump_count_until_merges_are_counted_by_type(self):
        stages = [dict(STAGES[1], target=dict(STAGES[1]["target"], by_pot_type=BY_TYPE))]
        p = progress(("2026-11-21T05:00:00+00:00", {"examples": 900, "spots": {"outside-hands-1": 700}}))
        svg = render(p, dict(CFG, stages=stages))
        self.assertIn(">700</tspan> of 1,000 of these spots solved", svg)
        self.assertNotIn("Single-raised pots", svg)
        self.assertEqual(height(svg), 340 + 34 + 42 + 24 + 8)

    def test_game_sizes_are_listed_once_examples_record_them(self):
        p = progress(("2026-11-21T05:00:00+00:00", {"examples": 100}),
                     ("2026-11-21T09:00:00+00:00", {"examples": 200, "sizes": {"0-6": 120, "6-12": 50, "19+": 30}}))
        svg = render(p, dict(CFG, stages=STAGES))
        minidom.parseString(svg)
        self.assertIn("Games by GPU memory needed:", svg)
        self.assertIn("under 6 GB 60% · 6 to 12 GB 25% · 12 to 19 GB 0% · over 19 GB 15% (of 200 that record it)", svg)
        self.assertEqual(height(svg), 340 + 34 + 2 * 42 + 24 + 26 + 8)
        self.assertNotIn("Games by GPU memory", render(progress(("2026-11-21T05:00:00+00:00", {"examples": 100})),
                                                       dict(CFG, stages=STAGES)))

    def test_the_shipped_config_draws(self):
        cfg = progress_chart.load_config()
        self.assertTrue(cfg["stages"])
        svg = render(progress(("2026-11-07T10:00:00+00:00", {"examples": 100})), cfg)
        minidom.parseString(svg)
        for s in cfg["stages"]:
            self.assertLessEqual(len(s["title"]) + 14, 112, s["title"])   # one line of the panel each
            self.assertLessEqual(len(s["for"]), 118, s["for"])
        self.assertIn("0</tspan> of 15,000 of these spots solved", svg)
        for s in cfg["stages"]:
            by = (s.get("target") or {}).get("by_pot_type")
            if by:
                self.assertEqual(sum(by.values()), s["target"]["solves"])   # the pot types add up to the target


if __name__ == "__main__":
    unittest.main()
