import time
import subprocess
import os
import sys

start_time = time.time()

# Paths
PATH_YT = 'yt_links/links.txt'
PATH_AUDIOS = 'yt_links/audio.txt'
AUDIO_DIR = 'audios'


def run_extraction():
    print('🚀 Downloading all audios (parallel)...')

    result = subprocess.run(
        ['python3', 'source/extraction.py', PATH_YT]
    )

    if result.returncode != 0:
        print("❌ Extraction failed")
        sys.exit(1)

    print("✅ Finished download from YouTube.\n")


def load_audio_list():
    # Case 1: audio.txt exists
    if os.path.exists(PATH_AUDIOS):
        print("📄 Loading audio list...")
        with open(PATH_AUDIOS, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    # Case 2: fallback
    print("⚠ audio.txt not found → scanning 'audios/' folder...")

    if not os.path.exists(AUDIO_DIR):
        print("❌ No audios found. Extraction failed.")
        sys.exit(1)

    files = [
        os.path.join(AUDIO_DIR, f)
        for f in os.listdir(AUDIO_DIR)
        if f.endswith(".wav")
    ]

    if not files:
        print("❌ No audio files found.")
        sys.exit(1)

    return files


def run_transcription(audio_files):
    print(f"\n🎧 Transcribing {len(audio_files)} files...\n")

    for audio in audio_files:
        print(f'>>> {audio}')

        subprocess.run([
            'python3',
            'source/transcribe_audio.py',
            audio
        ])


def cleanup():
    if os.path.exists(PATH_AUDIOS):
        os.remove(PATH_AUDIOS)
        print("\n🧹 Cleaned audio.txt")


def main():
    # Validate links file
    if not os.path.exists(PATH_YT):
        print(f"❌ Links file not found: {PATH_YT}")
        sys.exit(1)

    # STEP 1: Download (parallel inside extraction.py)
    run_extraction()

    # STEP 2: Load audios
    audio_files = load_audio_list()

    # STEP 3: Transcribe
    run_transcription(audio_files)

    # STEP 4: Cleanup
    cleanup()

    # TIME
    elapsed = time.time() - start_time
    print(f"\n⏱ Total time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()