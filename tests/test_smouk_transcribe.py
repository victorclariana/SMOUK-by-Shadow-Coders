import importlib.util
from pathlib import Path
import unittest


WORKER_PATH = Path(__file__).parents[1] / "scripts" / "smouk_transcribe.py"
SPEC = importlib.util.spec_from_file_location("smouk_transcribe", WORKER_PATH)
TRANSCRIBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRANSCRIBE)


class SubtitleCueTests(unittest.TestCase):
    SAMPLE = "El festival Altaveu ha homenatjat la primera diada de la democràcia"

    def assert_two_line_cues(self, cues):
        self.assertTrue(cues)
        for cue in cues:
            lines = cue["text"].splitlines()
            self.assertLessEqual(len(lines), 2)
            self.assertTrue(all(
                len(line) <= TRANSCRIBE.MAX_SUBTITLE_LINE_CHARS
                for line in lines
            ))

    def test_word_timestamps_never_create_a_third_line(self):
        words = [
            {"word": word, "start": index * 0.2, "end": (index + 1) * 0.2}
            for index, word in enumerate(self.SAMPLE.split())
        ]
        cues = TRANSCRIBE.words_to_cues(words)
        self.assert_two_line_cues(cues)
        self.assertEqual(
            " ".join(cue["text"].replace("\n", " ") for cue in cues),
            self.SAMPLE,
        )

    def test_segment_fallback_is_also_split_into_two_line_cues(self):
        cues = TRANSCRIBE.segments_to_cues([
            {"start": 0.0, "end": 3.0, "text": self.SAMPLE},
        ])
        self.assert_two_line_cues(cues)
        self.assertEqual(
            " ".join(cue["text"].replace("\n", " ") for cue in cues),
            self.SAMPLE,
        )


if __name__ == "__main__":
    unittest.main()
