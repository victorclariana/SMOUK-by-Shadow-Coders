"""Create SMOUK's isolated OpenVINO Catalan transcription runtime."""

import argparse
import os
import subprocess
import sys


MODEL_ID = "OpenVINO/whisper-large-v3-turbo-int4-ov"
MODEL_REVISION = "ae50b4d9a9dbaf16f2df59c23f3984e42f864dfc"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True)
    parser.add_argument("--model-dir", required=True)
    args = parser.parse_args()
    venv_dir = os.path.abspath(args.venv)
    model_root = os.path.abspath(args.model_dir)
    model_dir = os.path.join(model_root, "openvino-whisper-large-v3-turbo-int4-ov")
    python = os.path.join(venv_dir, "Scripts", "python.exe")

    if not os.path.isfile(python):
        print("Creating the transcription environment...", flush=True)
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    print("Installing the official OpenVINO runtime...", flush=True)
    install_env = os.environ.copy()
    install_env.pop("PIP_NO_INDEX", None)
    subprocess.check_call([
        python, "-m", "pip", "install", "--disable-pip-version-check",
        "openvino-genai==2026.4.0.0", "openvino==2026.4.0.0",
        "huggingface_hub==1.32.0", "soundfile==0.14.0", "numpy==2.5.3",
    ], env=install_env)

    if not os.path.isfile(os.path.join(model_dir, "openvino_encoder_model.bin")):
        print("Downloading the verified OpenVINO Whisper Turbo model...", flush=True)
        download = (
            "from huggingface_hub import snapshot_download; "
            "snapshot_download(" + repr(MODEL_ID) + ", revision=" +
            repr(MODEL_REVISION) + ", local_dir=" + repr(model_dir) + ", "
            "allow_patterns=['*.json','*.xml','*.bin','*.txt','*.model'])"
        )
        subprocess.check_call([python, "-c", download], env=install_env)
    print("SMOUK OpenVINO transcription engine is ready.", flush=True)


if __name__ == "__main__":
    main()
