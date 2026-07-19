import sys
import os
from faster_whisper import WhisperModel


# ==========================================
# VALIDATION
# ==========================================
if len(sys.argv) < 2:
    print("Usage: python transcribe_audio.py <AUDIO_FILE>")
    sys.exit(1)

audio_file = sys.argv[1]

if not os.path.isfile(audio_file):
    print("Error: audio file not found.")
    sys.exit(1)


# ==========================================
# CONFIG
# ==========================================
MODEL_SIZE = "tiny"        # tiny = fastest | base = better quality
DEVICE = "cpu"
COMPUTE_TYPE = "int8"      # faster on CPU
LANGUAGE = "en"            # change to "pt" if needed


# ==========================================
# LOAD MODEL
# ==========================================
print(f"Loading model ({MODEL_SIZE}, {COMPUTE_TYPE})...")

try:
    model = WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE
    )
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)


# ==========================================
# TRANSCRIPTION
# ==========================================
print("Transcribing audio...")

try:
    segments, info = model.transcribe(
        audio_file,
        language=LANGUAGE,
        beam_size=1  # faster decoding
    )
except Exception as e:
    print(f"Error during transcription: {e}")
    sys.exit(1)


# ==========================================
# BUILD TEXT
# ==========================================
text_parts = []

for segment in segments:
    text_parts.append(segment.text.strip())

text = " ".join(text_parts).strip()

if not text:
    print("Warning: empty transcription.")


# ==========================================
# OUTPUT FILE
# ==========================================
output_dir = "txts"
os.makedirs(output_dir, exist_ok=True)

base_name = os.path.splitext(os.path.basename(audio_file))[0]
output_file = os.path.join(output_dir, base_name + ".txt")

try:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text + "\n")
except Exception as e:
    print(f"Error saving file: {e}")
    sys.exit(1)


# ==========================================
# REMOVE AUDIO FILE
# ==========================================
try:
    if text:
        os.remove(audio_file)
        print(f"Removed audio file: {audio_file}")
    else:
        print("Audio not removed due to empty transcription.")
except Exception as e:
    print(f"Warning: could not remove audio file: {e}")


# ==========================================
# FINAL OUTPUT
# ==========================================
print("\n✅ Transcription completed!")
print(f"Saved to: {output_file}\n")
print("----- TRANSCRIPT -----")
