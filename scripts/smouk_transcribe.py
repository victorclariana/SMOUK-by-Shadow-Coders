"""Offline Catalan transcription worker used by the SMOUK Qt process."""

import argparse
import base64
import concurrent.futures
import json
import os
import re
import subprocess
import tempfile
import textwrap
import threading
import urllib.error
import urllib.request


DEFAULT_MODEL = "BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h"
DEFAULT_PROVIDER = "google"
DEFAULT_GOOGLE_MODEL = "chirp_3"
DEFAULT_GOOGLE_LOCATION = "eu"
DEFAULT_GOOGLE_CHUNK_SECONDS = 45.0
DEFAULT_GOOGLE_OVERLAP_SECONDS = 1.5
DEFAULT_GOOGLE_WORKERS = 3
DEFAULT_BEAM_SIZE = 3
MAX_SUBTITLE_LINE_CHARS = 26
MAX_SUBTITLE_CUE_CHARS = MAX_SUBTITLE_LINE_CHARS * 2
MIN_SUBTITLE_CUE_SECONDS = 1.0
APOSTROPHES = ("'", "’", "ʼ")
TRAILING_REPEAT_WORDS = {
    "a", "al", "de", "del", "el", "els", "en", "i", "la", "les",
    "lo", "que", "un", "una", "y",
}


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
    """Join brief cues to a neighbor when the resulting text remains readable."""
    cues = [dict(cue) for cue in cues]
    index = 0
    while index < len(cues):
        cue = cues[index]
        if cue["end"] - cue["start"] >= min_seconds:
            index += 1
            continue

        options = []
        for neighbor_index in (index - 1, index + 1):
            if not 0 <= neighbor_index < len(cues):
                continue
            left_index, right_index = sorted((index, neighbor_index))
            left, right = cues[left_index], cues[right_index]
            text = " ".join((left["text"] + " " + right["text"]).split())
            lines = _balanced_lines(text, width=line_width)
            start, end = min(left["start"], right["start"]), max(left["end"], right["end"])
            gap = max(0.0, right["start"] - left["end"])
            if (len(text) <= max_chars and len(lines) <= 2 and
                    all(len(line) <= line_width for line in lines) and
                    end - start <= max_seconds and gap <= 1.5):
                options.append((gap, left_index, right_index, text, start, end))

        if options:
            _gap, left_index, right_index, text, start, end = min(options)
            cues[left_index] = {
                "start": start, "end": end,
                "text": "\n".join(_balanced_lines(text, width=line_width)),
            }
            del cues[right_index]
            index = max(0, left_index - 1)
            continue

        # If an isolated, very short utterance cannot be merged without
        # overflowing two lines, keep it visible for at least one second.
        cues[index]["end"] = max(cue["end"], cue["start"] + min_seconds)
        if index + 1 < len(cues) and cues[index]["end"] > cues[index + 1]["start"]:
            cues[index + 1]["start"] = cues[index]["end"]
        index += 1
    return cues


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
    completed = subprocess.run(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace")[-1000:])
    return completed.stdout


def _media_duration(path):
    output = _run_media_command([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", os.path.abspath(path),
    ])
    return max(0.001, float(output.decode("ascii", errors="ignore").strip()))


def _google_seconds(value):
    """Parse Google Duration strings (for example ``1.250s``)."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "0").strip()
    if text.endswith("s"):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return 0.0


def _google_chunk(path, start, duration, temp_dir):
    output = os.path.join(temp_dir, "chunk-%012d.wav" % int(round(start * 1000)))
    _run_media_command([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", "%.3f" % start, "-t", "%.3f" % duration,
        "-i", os.path.abspath(path), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", output,
    ])
    return output


def _google_request(audio_path, project, location, recognizer, access_token,
                    model, chunk_start):
    endpoint = (
        "https://speech.googleapis.com/v2/projects/{}/locations/{}/recognizers/{}:recognize"
        .format(project, location, recognizer)
    )
    with open(audio_path, "rb") as handle:
        content = base64.b64encode(handle.read()).decode("ascii")
    payload = {
        "config": {
            "autoDecodingConfig": {},
            "languageCodes": ["ca-ES"],
            "model": model,
            "features": {
                "enableWordTimeOffsets": True,
                "enableAutomaticPunctuation": True,
            },
        },
        "content": content,
    }
    request = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + access_token,
                 "Content-Type": "application/json; charset=utf-8"},
        method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as ex:
        body = ex.read().decode("utf-8", errors="replace")
        raise RuntimeError("Google Speech API HTTP %s: %s" % (ex.code, body[-1000:]))
    words = []
    segments = []
    for result_item in result.get("results", []):
        alternatives = result_item.get("alternatives") or []
        if not alternatives:
            continue
        alternative = alternatives[0]
        result_words = alternative.get("words") or []
        if result_words:
            for item in result_words:
                word = str(item.get("word", "")).strip()
                if not word:
                    continue
                words.append({
                    "start": chunk_start + _google_seconds(item.get("startOffset")),
                    "end": chunk_start + _google_seconds(item.get("endOffset")),
                    "word": word,
                    "confidence": item.get("confidence", alternative.get("confidence")),
                })
        elif alternative.get("transcript"):
            segments.append({
                "start": chunk_start + _google_seconds(result_item.get("resultStartOffset")),
                "end": chunk_start + _google_seconds(result_item.get("resultEndOffset")),
                "text": alternative["transcript"],
            })
    return words, segments


def transcribe_google(path, project, location, recognizer, access_token,
                      model=DEFAULT_GOOGLE_MODEL,
                      chunk_seconds=DEFAULT_GOOGLE_CHUNK_SECONDS,
                      overlap_seconds=DEFAULT_GOOGLE_OVERLAP_SECONDS,
                      workers=DEFAULT_GOOGLE_WORKERS):
    """Transcribe Catalan audio through Chirp in parallel, with word offsets."""
    duration = _media_duration(path)
    chunks = []
    position = 0.0
    while position < duration:
        actual_start = max(0.0, position - (overlap_seconds if position else 0.0))
        actual_end = min(duration, position + chunk_seconds)
        chunks.append((actual_start, actual_end - actual_start, position))
        position += chunk_seconds
    _emit("status", text=(
        "Google Chirp 3: preparando %s fragmentos de %.0f s en paralelo…" %
        (len(chunks), chunk_seconds)))
    words, segments = [], []
    completed = 0
    lock = threading.Lock()
    with tempfile.TemporaryDirectory(prefix="smouk-google-") as temp_dir:
        def run(item):
            file_path = _google_chunk(path, item[0], item[1], temp_dir)
            return item[2], _google_request(
                file_path, project, location, recognizer, access_token,
                model, item[2] - (overlap_seconds if item[2] else 0.0))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futures = [pool.submit(run, item) for item in chunks]
            for future in concurrent.futures.as_completed(futures):
                _start, (chunk_words, chunk_segments) = future.result()
                words.extend(chunk_words)
                segments.extend(chunk_segments)
                with lock:
                    completed += 1
                    _emit("progress", value=int(round(completed * 85.0 / len(chunks))))
                    _emit("status", text=(
                        "Google Chirp 3: fragmento %s/%s transcrito…" %
                        (completed, len(chunks))))
                    partial_text = " ".join(item["word"] for item in sorted(
                        words, key=lambda value: value["start"])[-18:])
                    _emit("partial", words=len(words), text=partial_text)
    # Overlap is intentional for boundary accuracy; collapse duplicate words.
    deduped = []
    seen = set()
    for item in sorted(words, key=lambda value: (value["start"], value["end"])):
        key = (re.sub(r"\W+", "", item["word"].casefold()), round(item["start"], 1))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return duration, deduped, sorted(segments, key=lambda value: value["start"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cpu-threads", type=int, default=recommended_cpu_threads())
    parser.add_argument("--beam-size", type=int, default=DEFAULT_BEAM_SIZE)
    parser.add_argument("--provider", default=os.environ.get(
        "SMOUK_TRANSCRIPTION_PROVIDER", DEFAULT_PROVIDER))
    parser.add_argument("--google-project", default=os.environ.get("SMOUK_GOOGLE_PROJECT"))
    parser.add_argument("--google-location", default=os.environ.get(
        "SMOUK_GOOGLE_LOCATION", DEFAULT_GOOGLE_LOCATION))
    parser.add_argument("--google-recognizer", default=os.environ.get(
        "SMOUK_GOOGLE_RECOGNIZER", "_"))
    parser.add_argument("--google-access-token", default=os.environ.get(
        "SMOUK_GOOGLE_ACCESS_TOKEN"))
    parser.add_argument("--google-model", default=os.environ.get(
        "SMOUK_GOOGLE_MODEL", DEFAULT_GOOGLE_MODEL))
    parser.add_argument("--google-chunk-seconds", type=float, default=float(os.environ.get(
        "SMOUK_GOOGLE_CHUNK_SECONDS", DEFAULT_GOOGLE_CHUNK_SECONDS)))
    parser.add_argument("--google-overlap-seconds", type=float, default=float(os.environ.get(
        "SMOUK_GOOGLE_OVERLAP_SECONDS", DEFAULT_GOOGLE_OVERLAP_SECONDS)))
    parser.add_argument("--google-workers", type=int, default=int(os.environ.get(
        "SMOUK_GOOGLE_WORKERS", DEFAULT_GOOGLE_WORKERS)))
    args = parser.parse_args()

    if str(args.provider).casefold() == "google":
        if not args.google_project or not args.google_access_token:
            raise RuntimeError(
                "Google Chirp requires SMOUK_GOOGLE_PROJECT and "
                "SMOUK_GOOGLE_ACCESS_TOKEN (no audio was sent).")
        duration, words, fallback_segments = transcribe_google(
            args.input, args.google_project, args.google_location,
            args.google_recognizer, args.google_access_token, args.google_model,
            max(5.0, args.google_chunk_seconds),
            max(0.0, min(args.google_overlap_seconds, args.google_chunk_seconds / 2.0)),
            max(1, args.google_workers))
        args.model = "google-speech-to-text-v2/" + args.google_model
    else:
        duration = None
        words = None
        fallback_segments = None

    if words is None:
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
            beam_size=max(1, args.beam_size), vad_filter=True,
            vad_parameters={"threshold": 0.35, "speech_pad_ms": 500},
            word_timestamps=True, condition_on_previous_text=True,
        )
        duration = max(0.001, float(getattr(info, "duration", 0.0) or 0.0))
        words = []
        fallback_segments = []
        last_audio_percent = {"value": 0}
        stop_heartbeat = threading.Event()

        def report_long_segment():
            while not stop_heartbeat.wait(10.0):
                _emit("status", text=(
                    "Recognizing speech… audio processed through "
                    f"{last_audio_percent['value']}%. The current segment is still being decoded."
                ))

        heartbeat = threading.Thread(target=report_long_segment, daemon=True)
        heartbeat.start()
        try:
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
                last_audio_percent["value"] = min(
                    100, int(round(float(segment.end) * 100.0 / duration)))
                _emit("progress", value=int(round(last_audio_percent["value"] * 0.85)))
        finally:
            stop_heartbeat.set()
            heartbeat.join(timeout=1.0)

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
    }
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    _emit("progress", value=94)
    _emit("status", text="Saving the transcription and subtitle files…")
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    with open(os.path.splitext(output)[0] + ".srt", "w", encoding="utf-8") as handle:
        handle.write(srt)
    with open(os.path.splitext(output)[0] + ".vtt", "w", encoding="utf-8") as handle:
        handle.write("WEBVTT\n\n" + vtt)
    _emit("progress", value=99)
    _emit("complete", cues=len(cues), output=output)


if __name__ == "__main__":
    main()
