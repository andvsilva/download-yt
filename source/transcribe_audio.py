import sys
import os
import logging
from faster_whisper import WhisperModel
from tqdm import tqdm


# ==========================================
# CONFIG
# ==========================================
MODEL_SIZE = "tiny"        # tiny | base | small | medium | large
DEVICE = "cpu"             # "cpu" or "cuda"
COMPUTE_TYPE = "int8"      # int8 | float16
LANGUAGE = "en"            # None = auto
DELETE_AUDIO = True

OUTPUT_DIR = "txts"


# ==========================================
# LOGGING (IMPORTANT for tqdm)
# ==========================================
logging.basicConfig(
    level=logging.ERROR,  # 🔥 prevent tqdm break
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================================
# INPUT
# ==========================================
def get_input_path():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <AUDIO_FILE_OR_FOLDER>")
        sys.exit(1)
    return sys.argv[1]


def collect_audio_files(path):
    if os.path.isfile(path):
        return [path]

    if os.path.isdir(path):
        supported = (".mp3", ".wav", ".m4a", ".webm", ".mp4")
        return sorted([
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.lower().endswith(supported)
        ])

    print("❌ Invalid path.")
    sys.exit(1)


# ==========================================
# TRANSCRIBE
# ==========================================
def transcribe_file(model, audio_file):
    try:
        segments, _ = model.transcribe(
            audio_file,
            language=LANGUAGE,
            beam_size=1,
            vad_filter=True
        )

        text = " ".join(s.text.strip() for s in segments).strip()

        if not text:
            return "EMPTY", audio_file

        base = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(OUTPUT_DIR, base + ".txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text + "\n")

        if DELETE_AUDIO:
            os.remove(audio_file)

        return "OK", audio_file

    except Exception as e:
        return f"ERROR: {e}", audio_file


# ==========================================
# MAIN
# ==========================================
def main():
    input_path = get_input_path()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    audio_files = collect_audio_files(input_path)

    if not audio_files:
        print("⚠️ No audio files found.")
        return

    print(f"📂 Found {len(audio_files)} file(s)")

    # Load model once
    print(f"🧠 Loading model ({MODEL_SIZE}, {DEVICE}, {COMPUTE_TYPE})...")
    model = WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
        num_workers=4
    )

    results = []

    # 🔥 tqdm progress bar
    for audio in tqdm(audio_files, desc="Transcribing", unit="file"):
        result = transcribe_file(model, audio)
        results.append(result)

    # ==========================================
    # SUMMARY
    # ==========================================
    ok = sum(1 for r, _ in results if r == "OK")
    empty = sum(1 for r, _ in results if r == "EMPTY")
    errors = sum(1 for r, _ in results if "ERROR" in r)

    print("\n✅ Done!")
    print(f"✔ Success: {ok}")
    print(f"⚠️ Empty: {empty}")
    print(f"❌ Errors: {errors}")


if __name__ == "__main__":
    main()