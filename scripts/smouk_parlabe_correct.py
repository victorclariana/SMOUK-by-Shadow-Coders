"""Create an editable ParlaBE review layer for a BSC/Whisper JSON result.

The worker never changes cue timings. It groups the already-transcribed cues into
sentences, corrects each sentence conservatively, and returns both versions for
the Qt review dialog.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


MODEL_ID = "Oriolshhh/parlabe-mt5-ca-corrector"


def _workspace_root():
    return Path(__file__).resolve().parents[1]


def _load_runtime():
    root = _workspace_root()
    # Keep the first rollout usable with the verified isolated test runtime.
    # The setup script can later place the same packages in the SMOUK venv.
    fallback = root / ".parlabe-test" / "packages"
    if fallback.is_dir():
        sys.path.insert(0, str(fallback))
    try:
        import types
        import enum
        import importlib.machinery
        # Some Windows installations have an incompatible optional torchvision
        # package. ParlaBE is text-only, so expose only the enums Transformers
        # imports for optional image/video helpers.
        tv = types.ModuleType("torchvision")
        tv.__path__ = []
        tv.__spec__ = importlib.machinery.ModuleSpec("torchvision", loader=None, is_package=True)
        tr = types.ModuleType("torchvision.transforms")
        tr.__spec__ = importlib.machinery.ModuleSpec("torchvision.transforms", loader=None)
        class InterpolationMode(enum.Enum):
            NEAREST_EXACT = 0
            BOX = 4
            BILINEAR = 2
            HAMMING = 5
            BICUBIC = 3
            LANCZOS = 1
        tr.InterpolationMode = InterpolationMode
        tv.transforms = tr
        io = types.ModuleType("torchvision.io")
        io.__spec__ = importlib.machinery.ModuleSpec("torchvision.io", loader=None)
        tv.io = io
        sys.modules.update({"torchvision": tv, "torchvision.transforms": tr,
                            "torchvision.io": io})
    except Exception:
        pass
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    return AutoTokenizer, AutoModelForSeq2SeqLM


def _sentences_for_cues(cues):
    sentences = []
    current = []
    refs = []
    for index, cue in enumerate(cues):
        text = " ".join(str(cue.get("text", "")).split())
        if not text:
            continue
        # A single Whisper cue can contain two sentences. Keep the shared cue
        # reference on both sentence records; the Qt mapper merges them back
        # into that cue after review.
        parts = re.split(r"(?<=[.!?…])\s+", text)
        for part in parts:
            if not part:
                continue
            current.append(part)
            refs.append(index)
            if re.search(r"[.!?…][\"'»)]*$", part):
                sentences.append({"cue_indices": refs[:], "original": " ".join(current)})
                current, refs = [], []
    if current:
        sentences.append({"cue_indices": refs[:], "original": " ".join(current)})
    return sentences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-dir", required=True)
    args = parser.parse_args()
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    outputs = source.get("outputs", [])
    print(json.dumps({"event": "status", "text": "Loading ParlaBE Catalan correction model…"}, ensure_ascii=False), flush=True)
    AutoTokenizer, AutoModelForSeq2SeqLM = _load_runtime()
    model_root = Path(args.model_dir)
    cache_dir = model_root / "parlabe"
    fallback_cache = _workspace_root() / ".parlabe-test" / "model"
    if not cache_dir.exists() and fallback_cache.exists():
        cache_dir = fallback_cache
    local_only = cache_dir == fallback_cache
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=str(cache_dir),
                                               local_files_only=local_only)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID, cache_dir=str(cache_dir),
                                                  local_files_only=local_only)
    model.eval()

    review = []
    total = sum(len(_sentences_for_cues(result.get("cues", []))) for result in outputs)
    completed = 0
    for result_index, result in enumerate(outputs):
        for sentence_index, item in enumerate(_sentences_for_cues(result.get("cues", []))):
            original = item["original"]
            # This model card is trained with the short task prefix below. A
            # natural-language instruction makes mT5 echo the instruction on
            # some sentences, so conservatism is enforced in the review UI.
            prompt = "Corregeix la frase: " + original
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
            generated = model.generate(**inputs, max_new_tokens=128,
                                       num_beams=1, do_sample=False)
            corrected = tokenizer.decode(generated[0], skip_special_tokens=True).strip() or original
            if corrected.lower().startswith(("corregeix la frase:", "corregeix només")):
                corrected = original
            completed += 1
            print(json.dumps({"event": "status", "text":
                              f"Reviewing ParlaBE sentence {completed} of {total}…"},
                             ensure_ascii=False), flush=True)
            review.append({
                "result_index": result_index,
                "sentence_index": sentence_index,
                "cue_indices": item["cue_indices"],
                "original": original,
                "corrected": corrected,
            })
    payload = {"outputs": outputs, "sentences": review,
               "model": MODEL_ID, "times_preserved": True}
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"event": "complete", "sentences": len(review)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
