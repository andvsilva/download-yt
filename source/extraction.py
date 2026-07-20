import sys
import os
import re
from datetime import datetime
import logging
import tempfile
import subprocess
from multiprocessing import Pool, cpu_count

import pytubefix
import ffmpeg
from tqdm import tqdm


# ==========================================
# CONFIG
# ==========================================
OUTPUT_DIR = "audios"
LIST_DIR = "yt_links"
AUDIO_LIST_FILE = os.path.join(LIST_DIR, "audio.txt")

SAMPLE_RATE = 16000
CHANNELS = 1
MAX_WORKERS = max(1, cpu_count() - 1)


# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(processName)s - %(levelname)s - %(message)s"
)


# ==========================================
# HELPERS
# ==========================================
def sanitize_filename(title, max_length=100):
    clean = "".join(c for c in title if c.isalnum() or c in " _-")
    clean = re.sub(r"\s+", "_", clean)
    return clean[:max_length]


def generate_output_filename(title):
    safe_title = sanitize_filename(title)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return os.path.join(OUTPUT_DIR, f"{safe_title}_{timestamp}.wav")


def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception:
        print("❌ FFmpeg not found")
        sys.exit(1)


def create_directories():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LIST_DIR, exist_ok=True)


def create_youtube_object(url):
    return pytubefix.YouTube(url)


def get_best_audio_stream(yt):
    stream = yt.streams.filter(only_audio=True).first()
    if not stream:
        raise Exception("No audio stream found")
    return stream


def download_audio(stream):
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
            threads=0,
            loglevel="error"
        )
        .overwrite_output()
        .run()
    )


# ==========================================
# WORKER (PARALLEL SAFE)
# ==========================================
def process_video(youtube_url):
    try:
        yt = create_youtube_object(youtube_url)

        output_file = generate_output_filename(yt.title)

        if os.path.exists(output_file):
            return ("SKIP", output_file)

        stream = get_best_audio_stream(yt)

        temp_file = download_audio(stream)
        convert_to_wav(temp_file, output_file)

        os.remove(temp_file)

        return ("OK", output_file)

    except Exception as e:
        return ("ERROR", f"{youtube_url} | {e}")


# ==========================================
# MAIN
# ==========================================
def main():
    if len(sys.argv) < 2:
        print("Usage: python extraction.py <links.txt>")
        sys.exit(1)

    links_file = sys.argv[1]

    if not os.path.exists(links_file):
        print(f"❌ Links file not found: {links_file}")
        sys.exit(1)

    check_ffmpeg()
    create_directories()

    # Read links
    with open(links_file, "r") as f:
        yt_links = [line.strip() for line in f if line.strip()]

    if not yt_links:
        print("❌ No links found in file.")
        sys.exit(1)

    print(f"🚀 Processing {len(yt_links)} videos with {MAX_WORKERS} workers...\n")

    results = []

    # Parallel execution
    with Pool(MAX_WORKERS) as pool:
        for result in tqdm(
            pool.imap_unordered(process_video, yt_links),
            total=len(yt_links),
            desc="Downloading",
            unit="video"
        ):
            results.append(result)

    # ==========================================
    # WRITE AUDIO LIST (SAFE - AFTER POOL)
    # ==========================================
    success_files = [r[1] for r in results if r[0] == "OK"]

    with open(AUDIO_LIST_FILE, "w") as f:
        for path in success_files:
            f.write(path + "\n")

    # ==========================================
    # SUMMARY
    # ==========================================
    success = len(success_files)
    errors = sum(1 for r in results if r[0] == "ERROR")
    skipped = sum(1 for r in results if r[0] == "SKIP")

    print("\n✅ Done!")
    print(f"✔ Success: {success}")
    print(f"⚠ Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print(f"\n📄 Audio list saved at: {AUDIO_LIST_FILE}")


if __name__ == "__main__":
    main()