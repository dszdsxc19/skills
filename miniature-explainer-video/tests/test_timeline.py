"""Behavior checks for narration/shot separation and actual timing semantics."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL/"assets/project"))
from timeline_tools import build_timeline, locate_words

spec = importlib.util.spec_from_file_location("skill_scaffold", SKILL/"scripts/scaffold.py")
scaffold = importlib.util.module_from_spec(spec); spec.loader.exec_module(scaffold)


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.project = json.loads((SKILL/"assets/project/project.json").read_text())
        self.records = {"explain": {"provider": "none", "duration": 0, "words": []}}

    def test_one_segment_can_drive_multiple_shots(self):
        timeline = build_timeline(self.project, self.records)
        self.assertEqual(len(timeline["segments"]), 1)
        self.assertEqual(len(timeline["shots"]), 2)
        self.assertEqual(timeline["frames"], 180)
        self.assertEqual([e["time"] for e in timeline["events"]], [1.3, 2.8, 4.6])

    def test_repeated_anchor_selects_actual_second_word(self):
        words = [{"text": "等待", "start": .4, "end": .8},
                 {"text": "以后", "start": 1, "end": 1.4},
                 {"text": "等待", "start": 2.2, "end": 2.6}]
        result = locate_words(words, {"second": {"text": "等待", "occurrence": 2}})
        self.assertEqual(result["second"]["time"], 2.2)
        self.assertEqual(result["second"]["precision"], "word")

    def test_missing_actual_word_anchor_is_not_fabricated(self):
        with self.assertRaisesRegex(ValueError, "not present"):
            locate_words([{"text": "包裹", "start": .2, "end": .5}], {"missing": "检测器"})

    def test_audio_longer_than_plan_is_preserved_as_conflict(self):
        record = {"explain": {"provider": "file", "duration": 7, "words": []}}
        with self.assertRaisesRegex(ValueError, "Audio needs"):
            build_timeline(self.project, record)

    def test_gap_is_rejected(self):
        self.project["shots"][1]["in"] = 3.2
        with self.assertRaisesRegex(ValueError, "gap or overlap"):
            build_timeline(self.project, self.records)

    def test_action_can_continue_across_camera_cut(self):
        self.project["shots"][0]["beats"][1]["duration"] = .8
        timeline = build_timeline(self.project, self.records)
        event = next(e for e in timeline["events"] if e["id"] == "package-2")
        self.assertGreater(event["time"]+event["duration"], timeline["shots"][0]["end"])

    def test_same_event_is_not_assigned_to_two_shots(self):
        self.project["shots"][1]["beats"][0]["id"] = "package-1"
        with self.assertRaisesRegex(ValueError, "Duplicate event"):
            build_timeline(self.project, self.records)

    def test_manual_recording_cues_are_labelled_manual(self):
        self.project["segments"][0]["manual_cues"] = {"detector": 2.1}
        timeline = build_timeline(self.project, self.records)
        self.assertEqual(timeline["cues"]["explain.detector"], {"time": 2.1, "precision": "manual"})

    def test_scaffold_does_not_replace_existing_work(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/"existing"; target.mkdir()
            sentinel = target/"keep.txt"; sentinel.write_text("user work")
            with self.assertRaisesRegex(ValueError, "not empty"):
                scaffold.create(target)
            self.assertEqual(sentinel.read_text(), "user work")

    def test_unsafe_cache_identifier_is_rejected(self):
        self.project["segments"][0]["id"] = "../outside"
        with self.assertRaisesRegex(ValueError, "identifier"):
            build_timeline(self.project, self.records)


if __name__ == "__main__":
    unittest.main()
