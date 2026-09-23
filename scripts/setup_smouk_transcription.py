"""Create SMOUK's isolated BSC Catalan Whisper runtime."""

import argparse
import os
import subprocess
import sys


MODEL_ID = "BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True)
    parser.add_argument("--model-dir", required=True)
    args = parser.parse_args()
    venv_dir = os.path.abspath(args.venv)
    model_root = os.path.abspath(args.model_dir)
    python = os.path.join(venv_dir, "Scripts", "python.exe")

    if not os.path.isfile(python):
        print("Creating the transcription environment...", flush=True)
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    print("Installing the local Faster-Whisper runtime...", flush=True)
    install_env = os.environ.copy()
    install_env.pop("PIP_NO_INDEX", None)
    subprocess.check_call([
        python, "-m", "pip", "install", "--disable-pip-version-check",
        "faster-whisper==1.2.1", "ctranslate2==4.7.1",
    ], env=install_env)

    check = (
        "from faster_whisper import WhisperModel; "
        "WhisperModel(" + repr(MODEL_ID) + ", device='cpu', compute_type='int8', "
        "download_root=" + repr(model_root) + "); print('BSC model ready')"
    )
    subprocess.check_call([python, "-c", check], env=install_env)
    print("SMOUK BSC transcription engine is ready.", flush=True)


if __name__ == "__main__":
    main()
