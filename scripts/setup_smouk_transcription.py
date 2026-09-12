"""Create SMOUK's isolated faster-whisper runtime on Windows."""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True)
    args = parser.parse_args()
    venv_dir = os.path.abspath(args.venv)
    python = os.path.join(venv_dir, "Scripts", "python.exe")

    if not os.path.isfile(python):
        print("Creating the transcription environment...", flush=True)
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    print("Installing faster-whisper 1.2.1...", flush=True)
    subprocess.check_call([
        python, "-m", "pip", "install", "--disable-pip-version-check",
        "faster-whisper==1.2.1",
    ])
    print("SMOUK transcription engine is ready.", flush=True)


if __name__ == "__main__":
    main()
