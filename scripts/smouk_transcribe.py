"""Offline Catalan transcription worker used by the SMOUK Qt process."""

import argparse
import json
import os
import re
import subprocess
import textwrap


DEFAULT_MODEL = "openvino-whisper-large-v3-turbo-int4-ov"
# Keep inference off the graphics device used by OpenShot's Qt preview. On
# integrated Intel adapters, sharing the device between libopenshot and
# OpenVINO can terminate the Qt host with STATUS_FAIL_FAST_EXCEPTION. Users
# can opt in explicitly with SMOUK_OPENVINO_DEVICE=GPU.
DEFAULT_OPENVINO_DEVICE = "CPU"
DEFAULT_OPENVINO_CHUNK_SECONDS = 60.0
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


def _audio_chunk(path, start, duration, temp_dir, ffmpeg_path=None):
    output = os.path.join(temp_dir, "chunk-%012d.wav" % int(round(start * 1000)))
    _run_media_command([
        _tool_path("ffmpeg.exe", ffmpeg_path), "-hide_banner", "-loglevel", "error", "-y",
        "-ss", "%.3f" % start, "-t", "%.3f" % duration,
        "-i", os.path.abspath(path), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", output,
    ])
    return output


def _load_openvino_audio(path):
    import soundfile as sf
    import numpy as np
    audio, sample_rate = sf.read(path, dtype="float32")
    if getattr(audio, "ndim", 1) > 1:
        audio = np.mean(audio, axis=1)
    if int(sample_rate) != 16000:
        raise RuntimeError("OpenVINO requiere audio PCM mono a 16 kHz")
    return audio


def transcribe_openvino(path, model_dir, device=DEFAULT_OPENVINO_DEVICE,
                        chunk_seconds=DEFAULT_OPENVINO_CHUNK_SECONDS,
                        ffmpeg_path=None, temp_root=None):
    """Transcribe Catalan locally with the verified OpenVINO Turbo model."""
    import openvino as ov
    import openvino_genai as ov_genai

    duration = _media_duration(path, ffmpeg_path)
    chunks = []
    position = 0.0
    while position < duration:
        actual_end = min(duration, position + chunk_seconds)
        length = actual_end - position
        if length < 0.5:
            break
        chunks.append((position, length))
        position += chunk_seconds
    _emit("status", text=(
        "OpenVINO Whisper Turbo: preparando %s fragmentos de %.0f s…" %
        (len(chunks), chunk_seconds)))
    model_path = os.path.abspath(model_dir)
    if not os.path.isdir(model_path):
        raise RuntimeError("No se encuentra el modelo OpenVINO: %s" % model_path)
    available = {str(item).upper() for item in ov.Core().available_devices}
    selected_device = str(device or "AUTO").upper()
    if selected_device == "GPU" and "GPU" not in available:
        selected_device = "CPU"
    _emit("status", text=("Cargando OpenVINO Whisper Turbo en %s…" % selected_device))
    pipe = ov_genai.WhisperPipeline(model_path, selected_device)
    config = ov_genai.WhisperGenerationConfig()
    config.language = "<|ca|>"
    config.task = "transcribe"
    config.return_timestamps = False
    config.max_new_tokens = 448
    words, segments = [], []
    completed = 0
    temp_dir = os.path.join(temp_root or os.path.dirname(os.path.abspath(path)),
                            ".smouk-openvino-audio")
    os.makedirs(temp_dir, exist_ok=True)
    for start, length in chunks:
        file_path = _audio_chunk(path, start, length, temp_dir, ffmpeg_path)
        audio = _load_openvino_audio(file_path)
        decoded = pipe.generate(audio, config)
        text = " ".join(str(item).strip() for item in decoded.texts).strip()
        if text:
            segments.append({"start": start, "end": start + length, "text": text})
        completed += 1
        _emit("progress", value=int(round(completed * 85.0 / len(chunks))))
        _emit("status", text=(
            "OpenVINO Whisper Turbo: fragmento %s/%s transcrito…" %
            (completed, len(chunks))))
        _emit("partial", words=len(text.split()), text=text[-400:])
        try:
            os.remove(file_path)
        except OSError:
            pass
    return duration, words, sorted(segments, key=lambda value: value["start"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--openvino-device", default=os.environ.get(
        "SMOUK_OPENVINO_DEVICE", DEFAULT_OPENVINO_DEVICE))
    parser.add_argument("--openvino-chunk-seconds", type=float, default=float(
        os.environ.get("SMOUK_OPENVINO_CHUNK_SECONDS", DEFAULT_OPENVINO_CHUNK_SECONDS)))
    parser.add_argument("--ffmpeg-path", default=os.environ.get("SMOUK_FFMPEG_PATH"))
    args = parser.parse_args()

    model_path = os.path.join(os.path.abspath(args.model_dir), args.model)
    duration, words, fallback_segments = transcribe_openvino(
        args.input, model_path, args.openvino_device,
        max(5.0, args.openvino_chunk_seconds), args.ffmpeg_path,
        os.path.dirname(os.path.abspath(args.output)))

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
