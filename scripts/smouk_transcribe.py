"""Offline Catalan transcription worker used by the SMOUK Qt process."""

import argparse
import json
import os
import textwrap


DEFAULT_MODEL = "BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h"


def recommended_cpu_threads(logical_cpus=None):
    """Use most of a workstation CPU without starving the SMOUK interface."""
    logical_cpus = int(logical_cpus or os.cpu_count() or 1)
    if logical_cpus <= 4:
        return logical_cpus
    return min(10, logical_cpus - 2)


def _emit(event, **values):
    print(json.dumps({"event": event, **values}, ensure_ascii=False), flush=True)


def _timecode(seconds):
    milliseconds = max(0, int(round(float(seconds) * 1000.0)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _balanced_lines(text, width=42):
    lines = textwrap.wrap(
        " ".join(str(text).split()), width=width,
        break_long_words=False, break_on_hyphens=False,
    )
    if len(lines) <= 1:
        return lines
    if len(lines) == 2:
        return lines
    return [lines[0], " ".join(lines[1:])]


def words_to_cues(words, max_chars=84, max_seconds=6.0, pause_seconds=0.55):
    """Group timestamped words into readable two-line subtitle cues."""
    clean = []
    for word in words:
        text = str(word.get("word", "")).strip()
        if not text:
            continue
        clean.append({
            "start": float(word.get("start", 0.0)),
            "end": float(word.get("end", word.get("start", 0.0))),
            "word": text,
        })

    cues = []
    current = []

    def finish():
        if not current:
            return
        cue_text = " ".join(item["word"] for item in current)
        cues.append({
            "start": current[0]["start"],
            "end": max(current[-1]["end"], current[0]["start"] + 0.2),
            "text": "\n".join(_balanced_lines(cue_text)),
        })
        current.clear()

    for word in clean:
        proposed = " ".join([item["word"] for item in current] + [word["word"]])
        long_pause = bool(current and word["start"] - current[-1]["end"] >= pause_seconds)
        too_long = bool(current and (
            len(proposed) > max_chars or
            word["end"] - current[0]["start"] > max_seconds
        ))
        sentence_break = bool(current and current[-1]["word"].endswith((".", "?", "!")) and
                              word["start"] - current[-1]["end"] >= 0.18)
        if long_pause or too_long or sentence_break:
            finish()
        current.append(word)
    finish()
    return cues


def cues_to_srt(cues):
    blocks = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(
            f"{index}\n{_timecode(cue['start'])} --> {_timecode(cue['end'])}\n{cue['text']}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cpu-threads", type=int, default=recommended_cpu_threads())
    parser.add_argument("--beam-size", type=int, default=1)
    args = parser.parse_args()

    from faster_whisper import WhisperModel

    _emit("status", text="Loading the Catalan model (the first run downloads it)...")
    model = WhisperModel(
        args.model, device="cpu", compute_type="int8",
        cpu_threads=max(1, args.cpu_threads),
        download_root=os.path.abspath(args.model_dir),
    )
    _emit("status", text=(
        f"Transcribing Catalan audio with {max(1, args.cpu_threads)} CPU threads..."
    ))
    segments, info = model.transcribe(
        os.path.abspath(args.input), language="ca", task="transcribe",
        beam_size=max(1, args.beam_size), vad_filter=True, word_timestamps=True,
        condition_on_previous_text=False,
    )
    duration = max(0.001, float(getattr(info, "duration", 0.0) or 0.0))
    words = []
    fallback_segments = []
    for segment in segments:
        fallback_segments.append({
            "start": float(segment.start), "end": float(segment.end),
            "text": str(segment.text).strip(),
        })
        for word in getattr(segment, "words", None) or []:
            words.append({
                "start": float(word.start), "end": float(word.end),
                "word": str(word.word).strip(),
            })
        _emit("progress", value=min(99, int(round(float(segment.end) * 100.0 / duration))))

    cues = words_to_cues(words) if words else fallback_segments
    srt = cues_to_srt(cues)
    result = {
        "source": os.path.abspath(args.input),
        "language": "ca",
        "model": args.model,
        "duration": duration,
        "cues": cues,
        "srt": srt,
    }
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    with open(os.path.splitext(output)[0] + ".srt", "w", encoding="utf-8") as handle:
        handle.write(srt)
    _emit("complete", cues=len(cues), output=output)


if __name__ == "__main__":
    main()
