"""Offline Catalan transcription worker used by the SMOUK Qt process."""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import traceback


DEFAULT_MODEL = "BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h"
DEFAULT_BEAM_SIZE = 3
MAX_SUBTITLE_LINE_CHARS = 26
MAX_SUBTITLE_CUE_CHARS = MAX_SUBTITLE_LINE_CHARS * 2
MIN_SUBTITLE_CUE_SECONDS = 1.0
APOSTROPHES = ("'", "’", "ʼ")
TRAILING_REPEAT_WORDS = {
    "a", "al", "de", "del", "el", "els", "en", "i", "la", "les",
    "lo", "que", "un", "una", "y",
}


def _emit(event, **values):
    print(json.dumps({"event": event, **values}, ensure_ascii=False), flush=True)


def _trace(step, **details):
    """Emit a machine-readable breadcrumb before every native boundary."""
    _emit("trace", step=step, **details)


def _timecode(seconds):
    milliseconds = max(0, int(round(float(seconds) * 1000.0)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def recommended_cpu_threads(logical_cpus=None):
    """Leave two logical CPUs free for the editor while BSC decodes."""
    logical_cpus = int(logical_cpus or os.cpu_count() or 1)
    return logical_cpus if logical_cpus <= 4 else min(10, logical_cpus - 2)


def _normalized_token(token):
    return str(token).strip(".,;:!?¿¡()[]{}\"“”'’ʼ").casefold()


def _trailing_hallucination_start(tokens):
    """Find a repeated Catalan function-word tail ending in a stray i/y."""
    normalized = [_normalized_token(token) for token in tokens]
    if len(normalized) < 4 or normalized[-1] not in {"i", "y"}:
        return None
    if len(normalized[-1]) != 1:
        return None
    for index in range(len(normalized) - 3, max(-1, len(normalized) - 6), -1):
        if (normalized[index] in TRAILING_REPEAT_WORDS and
                normalized[index] == normalized[index + 1] and
                all(len(token) <= 3 for token in normalized[index + 2:])):
            return index
    return None


def trim_hallucinated_tail(text):
    """Remove only a duplicated function-word tail ending in a stray letter."""
    tokens = str(text).split()
    start = _trailing_hallucination_start(tokens)
    if start is None:
        return str(text).strip()
    kept = tokens[:start]
    if kept:
        kept[-1] = re.sub(r"[,;:]+$", ".", kept[-1])
    return " ".join(kept)


def _balanced_lines(text, width=MAX_SUBTITLE_LINE_CHARS):
    """Wrap for a vertical canvas and avoid orphaned Catalan prepositions."""
    clean = " ".join(str(text).split())
    if not clean:
        return []
    if len(clean) <= width:
        return [clean]
    words = clean.split()
    candidates = []
    weak_endings = {"a", "amb", "d'", "de", "del", "dels", "el", "els",
                    "i", "la", "les", "per", "pel", "pels"}
    for index in range(1, len(words)):
        left = " ".join(words[:index])
        right = " ".join(words[index:])
        if len(left) > width or len(right) > width:
            continue
        penalty = 20 if words[index - 1].lower() in weak_endings else 0
        candidates.append((abs(len(left) - len(right)) + penalty, index, left, right))
    if candidates:
        _score, _index, left, right = min(candidates)
        return [left, right]
    return textwrap.wrap(clean, width=width, break_long_words=False,
                         break_on_hyphens=False)


def words_to_cues(words, max_chars=MAX_SUBTITLE_CUE_CHARS,
                  max_seconds=6.0, pause_seconds=0.55,
                  line_width=MAX_SUBTITLE_LINE_CHARS,
                  min_seconds=MIN_SUBTITLE_CUE_SECONDS):
    """Group timestamped words into readable two-line subtitle cues."""
    clean = []
    for word in words:
        text = str(word.get("word", "")).strip()
        if not text:
            continue
        item = {
            "start": float(word.get("start", 0.0)),
            "end": float(word.get("end", word.get("start", 0.0))),
            "word": text,
        }
        # Whisper may timestamp the two sides of a Catalan contraction as
        # separate tokens (for example, "d" + "'acollida"). Keep the whole
        # apostrophized word indivisible for both cue and line wrapping.
        if clean and (clean[-1]["word"].endswith(APOSTROPHES) or
                      item["word"].startswith(APOSTROPHES)):
            clean[-1]["word"] += item["word"]
            clean[-1]["end"] = max(clean[-1]["end"], item["end"])
        else:
            clean.append(item)

    cues = []
    current = []

    def finish():
        if not current:
            return
        cue_text = " ".join(item["word"] for item in current)
        cues.append({
            "start": current[0]["start"],
            "end": max(current[-1]["end"], current[0]["start"] + 0.2),
            "text": "\n".join(_balanced_lines(cue_text, width=line_width)),
        })
        current.clear()

    for word in clean:
        proposed = " ".join([item["word"] for item in current] + [word["word"]])
        current_duration = (current[-1]["end"] - current[0]["start"]
                            if current else 0.0)
        long_pause = bool(current and current_duration >= min_seconds and
                          word["start"] - current[-1]["end"] >= pause_seconds)
        proposed_lines = _balanced_lines(proposed, width=line_width)
        too_long = bool(current and (
            len(proposed) > max_chars or
            len(proposed_lines) > 2 or
            any(len(line) > line_width for line in proposed_lines) or
            word["end"] - current[0]["start"] > max_seconds
        ))
        sentence_break = bool(current and current_duration >= min_seconds and
                              current[-1]["word"].endswith((".", "?", "!")) and
                              word["start"] - current[-1]["end"] >= 0.18)
        if long_pause or too_long or sentence_break:
            finish()
        current.append(word)
    finish()
    return _merge_short_cues(cues, max_chars=max_chars, max_seconds=max_seconds,
                             line_width=line_width, min_seconds=min_seconds)


def _merge_short_cues(cues, max_chars=MAX_SUBTITLE_CUE_CHARS,
                      max_seconds=6.0, line_width=MAX_SUBTITLE_LINE_CHARS,
                      min_seconds=MIN_SUBTITLE_CUE_SECONDS):
    """Make each cue readable in one bounded pass.

    Older versions repeatedly merged a short cue with either neighbour and
    restarted the loop. With dense word timestamps that could oscillate
    forever after Whisper had already completed. Subtitle timing must never
    depend on that optional cosmetic merge.
    """
    result = []
    for cue in cues:
        item = dict(cue)
        item["end"] = max(float(item["end"]), float(item["start"]) + min_seconds)
        if result and item["start"] < result[-1]["end"]:
            item["start"] = result[-1]["end"]
        if item["end"] <= item["start"]:
            continue
        result.append(item)
    return result


def segments_to_cues(segments):
    """Convert segment-only output to word timings and enforce two-line cues."""
    estimated_words = []
    for segment in segments:
        words = str(segment.get("text", "")).split()
        if not words:
            continue
        start = float(segment.get("start", 0.0))
        end = max(start + 0.2, float(segment.get("end", start)))
        weights = [max(1, len(word)) for word in words]
        total_weight = float(sum(weights))
        elapsed_weight = 0.0
        for word, weight in zip(words, weights):
            word_start = start + (end - start) * elapsed_weight / total_weight
            elapsed_weight += weight
            word_end = start + (end - start) * elapsed_weight / total_weight
            estimated_words.append({
                "start": word_start, "end": word_end, "word": word,
            })
    return words_to_cues(estimated_words)


def _usable_word(text):
    return bool(re.search(r"[\wÀ-ÖØ-öø-ÿ]", str(text), flags=re.UNICODE))


def _stable_segment_words(segment):
    """Preserve valid Whisper word marks and repair only an invalid word."""
    start, end = float(segment["start"]), float(segment["end"])
    words = [dict(item) for item in segment.get("words", []) if _usable_word(item.get("word"))]
    if not words:
        return []
    repaired = []
    previous_end = start
    for index, item in enumerate(words):
        item["start"] = max(previous_end, float(item["start"]))
        item["end"] = float(item["end"])
        next_start = (float(words[index + 1]["start"])
                      if index + 1 < len(words) else end)
        # Faster-Whisper can assign an entire silent stretch to one ordinary
        # word. Clamp that one word only: the surrounding words retain their
        # native, accurate marks instead of being shifted over the segment.
        if item["end"] <= item["start"] or item["end"] - item["start"] > 2.5:
            item["end"] = min(next_start, item["start"] + 1.0)
            _emit("trace", step="word_timestamp.clamped", word=item["word"],
                  start=item["start"], end=item["end"])
        if item["end"] > item["start"]:
            repaired.append(item)
            previous_end = item["end"]
    return repaired


def cues_to_srt(cues):
    blocks = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(
            f"{index}\n{_timecode(cue['start'])} --> {_timecode(cue['end'])}\n{cue['text']}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def cues_to_vtt(cues):
    """Build the timestamp-only format expected by OpenShot's Caption effect."""
    blocks = []
    for cue in cues:
        start = _timecode(cue["start"]).replace(",", ".")
        end = _timecode(cue["end"]).replace(",", ".")
        blocks.append(f"{start} --> {end}\n{cue['text']}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def _run_media_command(command):
    _trace("media.command.start", command=[str(item) for item in command])
    completed = subprocess.run(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    _trace("media.command.finish", returncode=completed.returncode)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace")[-1000:])
    return completed.stdout


def _tool_path(name, ffmpeg_path=None):
    if ffmpeg_path:
        sibling = os.path.join(os.path.dirname(os.path.abspath(ffmpeg_path)), name)
        if os.path.isfile(sibling):
            return sibling
    return name


def _media_duration(path, ffmpeg_path=None):
    output = _run_media_command([
        _tool_path("ffprobe.exe", ffmpeg_path), "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", os.path.abspath(path),
    ])
    return max(0.001, float(output.decode("ascii", errors="ignore").strip()))


def transcribe_bsc(path, model_dir, ffmpeg_path, temp_root, source_start, source_duration,
                   model_name=DEFAULT_MODEL, beam_size=DEFAULT_BEAM_SIZE):
    """Extract exactly the timeline IN–OUT and transcribe it with BSC Whisper."""
    full_duration = _media_duration(path, ffmpeg_path)
    source_start = max(0.0, float(source_start or 0.0))
    if source_start >= full_duration:
        raise RuntimeError("El IN del clip queda fuera de la duración del vídeo")
    duration = min(full_duration - source_start,
                   float(source_duration) if source_duration is not None else full_duration)
    duration = max(0.001, duration)
    temp_dir = os.path.join(temp_root, ".smouk-bsc-audio")
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, "timeline-in-out.wav")
    _emit("trace", step="timeline_range", source_start=source_start,
          source_end=source_start + duration, duration=duration)
    _emit("status", text="Extracting the exact Timeline IN–OUT audio…")
    _run_media_command([
        _tool_path("ffmpeg.exe", ffmpeg_path), "-hide_banner", "-loglevel", "error", "-y",
        "-ss", "%.6f" % source_start, "-t", "%.6f" % duration,
        "-i", os.path.abspath(path), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", audio_path,
    ])
    from faster_whisper import WhisperModel
    threads = recommended_cpu_threads()
    _emit("status", text="Loading BSC Catalan Whisper…")
    model = WhisperModel(model_name, device="cpu", compute_type="int8",
                         cpu_threads=threads, download_root=os.path.abspath(model_dir))
    _emit("status", text="Transcribing the extracted Timeline audio in Catalan…")
    raw_segments, words = [], []
    segments, info = model.transcribe(
        audio_path, language="ca", task="transcribe", beam_size=max(1, int(beam_size)),
        vad_filter=True, vad_parameters={"threshold": 0.35, "speech_pad_ms": 500},
        word_timestamps=True, condition_on_previous_text=True,
    )
    for segment in segments:
        raw = {"start": float(segment.start), "end": float(segment.end),
               "text": str(segment.text).strip(), "words": []}
        for word in getattr(segment, "words", None) or []:
            raw["words"].append({"start": float(word.start), "end": float(word.end),
                                 "word": str(word.word).strip()})
        words.extend(_stable_segment_words(raw))
        raw_segments.append(raw)
        percent = int(round(min(duration, raw["end"]) * 85.0 / duration))
        _emit("progress", value=percent)
        _emit("partial", words=len(raw["words"]), text=raw["text"])
    try:
        os.remove(audio_path)
    except OSError:
        pass
    return duration, words, raw_segments, {
        "source_start": source_start, "source_end": source_start + duration,
        "audio_duration": float(getattr(info, "duration", duration) or duration),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--beam-size", type=int, default=DEFAULT_BEAM_SIZE)
    parser.add_argument("--ffmpeg-path", default=os.environ.get("SMOUK_FFMPEG_PATH"))
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--duration", type=float, default=None)
    args = parser.parse_args()

    try:
        duration, words, fallback_segments, timeline_range = transcribe_bsc(
            args.input, args.model_dir, args.ffmpeg_path,
            os.path.dirname(os.path.abspath(args.output)), args.start,
            args.duration, args.model, args.beam_size)
    except Exception as exc:
        _emit("error", message=str(exc), traceback=traceback.format_exc())
        raise

    _emit("progress", value=90)
    _emit("status", text="Formatting two-line subtitles and checking reading times…")
    if words:
        tail_start = _trailing_hallucination_start([item["word"] for item in words])
        if tail_start is not None:
            words = words[:tail_start]
            if words:
                words[-1]["word"] = re.sub(r"[,;:]+$", ".", words[-1]["word"])
    elif fallback_segments:
        fallback_segments[-1]["text"] = trim_hallucinated_tail(
            fallback_segments[-1]["text"])

    cues = words_to_cues(words) if words else segments_to_cues(fallback_segments)
    srt = cues_to_srt(cues)
    vtt = cues_to_vtt(cues)
    result = {
        "source": os.path.abspath(args.input),
        "language": "ca",
        "model": args.model,
        "duration": duration,
        "cues": cues,
        "srt": srt,
        "vtt": vtt,
        "timeline_range": timeline_range,
        "raw_segments": fallback_segments,
    }
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    _emit("progress", value=94)
    _emit("status", text="Saving the transcription and subtitle files…")
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    raw_output = os.path.splitext(output)[0] + ".whisper-raw.json"
    with open(raw_output, "w", encoding="utf-8") as handle:
        json.dump({"source": result["source"], "timeline_range": timeline_range,
                   "segments": fallback_segments}, handle, ensure_ascii=False, indent=2)
    _emit("trace", step="raw_transcript.saved", path=raw_output,
          segments=len(fallback_segments))
    with open(os.path.splitext(output)[0] + ".srt", "w", encoding="utf-8") as handle:
        handle.write(srt)
    with open(os.path.splitext(output)[0] + ".vtt", "w", encoding="utf-8") as handle:
        handle.write("WEBVTT\n\n" + vtt)
    _emit("progress", value=99)
    _emit("complete", cues=len(cues), output=output)


if __name__ == "__main__":
    main()
