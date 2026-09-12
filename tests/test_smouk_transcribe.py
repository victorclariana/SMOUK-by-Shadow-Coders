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

    def test_apostrophized_words_are_never_split_between_whisper_tokens(self):
        words = [
            {"word": "d", "start": 0.0, "end": 0.1},
            {"word": "'odi", "start": 0.1, "end": 0.45},
            {"word": "d'", "start": 0.5, "end": 0.6},
            {"word": "acollida", "start": 0.6, "end": 1.1},
        ]
        cues = TRANSCRIBE.words_to_cues(words)
        rendered = " ".join(cue["text"].replace("\n", " ") for cue in cues)
        self.assertEqual(rendered, "d'odi d'acollida")
        self.assertTrue(all("d\n'odi" not in cue["text"] for cue in cues))
        self.assert_two_line_cues(cues)

    def test_short_twelve_frame_cue_is_kept_readable(self):
        cues = TRANSCRIBE.words_to_cues([
            {"word": "Sí.", "start": 30.05, "end": 30.53},
        ])
        self.assertEqual(len(cues), 1)
        self.assertGreaterEqual(
            cues[0]["end"] - cues[0]["start"],
            TRANSCRIBE.MIN_SUBTITLE_CUE_SECONDS,
        )

    def test_caption_vtt_has_no_srt_cue_numbers(self):
        cues = TRANSCRIBE.words_to_cues([
            {"word": "Primer", "start": 0.0, "end": 0.6},
            {"word": "text.", "start": 0.6, "end": 1.2},
            {"word": "Segon", "start": 1.3, "end": 1.9},
            {"word": "text.", "start": 1.9, "end": 2.5},
        ])
        vtt = TRANSCRIBE.cues_to_vtt(cues)
        self.assertNotIn("\n1\n", vtt)
        self.assertNotIn("\n2\n", vtt)
        self.assertIn("00:00:00.000 -->", vtt)


if __name__ == "__main__":
    unittest.main()
