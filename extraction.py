import sys
import os
import re
from datetime import datetime
import logging
import tempfile
import subprocess

import pytubefix
import ffmpeg


# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_DIR = "audios"
SAMPLE_RATE = 16000
CHANNELS = 1


# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def validate_args():
    if len(sys.argv) < 2:
        print("Usage: python script.py <YOUTUBE_URL>")
        sys.exit(1)
    return sys.argv[1]


def check_ffmpeg():
    """Check if FFmpeg is installed correctly (no fake errors)."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception:
        logging.error("❌ FFmpeg not found. Install it first.")
        sys.exit(1)


def create_output_directory():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def sanitize_filename(title, max_length=100):
    clean = "".join(c for c in title if c.isalnum() or c in " _-")
    clean = clean.strip()
    clean = re.sub(r"\s+", "_", clean)
    clean = re.sub(r"_+", "_", clean)
    return clean[:max_length]


def generate_output_filename(title):
    safe_title = sanitize_filename(title)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return os.path.join(OUTPUT_DIR, f"{safe_title}_{timestamp}.wav")


def create_youtube_object(url, retries=3):
    for i in range(retries):
        try:
            return pytubefix.YouTube(url)
        except Exception:
            if i == retries - 1:
                raise
            logging.warning(f"Retrying YouTube connection... ({i+1})")


def get_best_audio_stream(yt):
    # Faster (no sorting)
    stream = yt.streams.filter(only_audio=True).first()

    if not stream:
        raise RuntimeError("No audio stream found.")

    return stream


def download_audio(stream):
    # Safe temporary file
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp.close()
    return stream.download(filename=temp.name)


def convert_to_wav(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(
            output_file,
            format="wav",
            acodec="pcm_s16le",
            ac=CHANNELS,
            ar=SAMPLE_RATE,
            threads=0,          # 🔥 use all CPU cores
            loglevel="error"
        )
        .overwrite_output()
        .run()
    )


def save_output_reference(filename):
    with open("filename_audio.txt", "a") as f:
        f.write(filename + "\n")


# ==========================================
# MAIN
# ==========================================
def main():
    youtube_url = validate_args()

    check_ffmpeg()
    create_output_directory()

    try:
        logging.info("Connecting to YouTube...")
        yt = create_youtube_object(youtube_url)

        logging.info(f"Video title: {yt.title}")

        output_file = generate_output_filename(yt.title)

        if os.path.exists(output_file):
            logging.warning("⚠️ File already exists. Skipping...")
            return

        logging.info("Fetching audio stream...")
        stream = get_best_audio_stream(yt)

        logging.info("Downloading audio...")
        temp_file = download_audio(stream)

        logging.info("Converting to WAV...")
        convert_to_wav(temp_file, output_file)

        os.remove(temp_file)

        save_output_reference(output_file)

        logging.info(f"✅ Audio saved at: {output_file}")

    except pytubefix.exceptions.PytubeError as e:
        logging.error(f"YouTube error: {e}")
        sys.exit(1)

    except ffmpeg.Error as e:
        logging.error(f"FFmpeg error: {e}")
        sys.exit(1)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()