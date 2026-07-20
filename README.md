Here’s a complete and clean `README.md` for your project, explaining everything clearly:

---

# 🎧 YouTube Audio Extraction + Transcription Pipeline

This project downloads audio from YouTube videos, converts it to WAV format, and transcribes it into text using speech recognition.

---

## 🚀 Features

* ✅ Download audio from YouTube links
* ✅ Convert audio to high-quality WAV (16kHz mono)
* ✅ Batch processing (multiple links)
* ✅ Automatic transcription to text files
* ✅ Clean filenames (no spaces/issues)
* ✅ Logging and error handling
* ✅ Optimized for performance (multi-core FFmpeg)

---

## 📁 Project Structure

```
project/
│
├── yt_links/
│   ├── links.txt        # List of YouTube URLs
│   └── audio.txt        # Generated audio file paths
│
├── source/
│   ├── extraction.py    # Download + convert audio
│   └── transcribe_audio.py  # Transcription script
│
├── audios/              # Output WAV files
├── txts/                # Transcribed text files
│
└── main.py              # Master script (runs everything)
```

---

## ⚙️ Requirements

### 1. Python

* Python 3.9+

### 2. Install dependencies

```bash
pip install pytubefix ffmpeg-python openai-whisper
```

---

### 3. Install FFmpeg (REQUIRED)

#### Ubuntu / Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Verify installation

```bash
ffmpeg -version
```

---

## 📌 How to Use

### Step 1 — Add YouTube Links

Edit the file:

```
yt_links/links.txt
```

Example:

```
https://www.youtube.com/watch?v=XXXXX
https://www.youtube.com/watch?v=YYYYY
```

---

### Step 2 — Run the Pipeline

```bash
python3 main.py
```

---

## 🔄 What Happens Internally

1. Reads all YouTube links
2. Downloads audio (temporary file)
3. Converts to WAV (16kHz mono)
4. Saves to `audios/`
5. Stores file paths in `yt_links/audio.txt`
6. Transcribes each audio
7. Saves text output in `txts/`
8. Cleans temporary files

---

## 🧠 Transcription (Whisper)

* Uses OpenAI Whisper
* Automatically detects language
* Outputs `.txt` files

---

## ⚡ Performance Tips

* Use GPU for Whisper (if available):

```python
model = whisper.load_model("base", device="cuda")
```

* Faster models:

  * `tiny` → fastest
  * `base` → balanced
  * `small` → better accuracy
  * `medium/large` → high accuracy (slow)

---

## 🛠 Example: Run Transcription Only

```bash
python3 source/transcribe_audio.py audios/example.wav
```

---

## ❌ Common Errors

### FFmpeg not found

```
❌ FFmpeg not found. Install it first.
```

✔ Fix:

```bash
sudo apt install ffmpeg
```

---

### Permission denied (Git)

```
Permission denied (publickey)
```

✔ Fix SSH or use HTTPS repo

---

### Audio not found

```
Error: audio file not found
```

✔ Check path or filename

---

## 🧹 Cleanup

The script automatically removes:

* Temporary files
* `yt_links/audio.txt` after processing

---

## 📈 Possible Improvements

* Save subtitles (.srt)
* Language filtering
* Silence trimming for TTS training
* Chunk audio into 10–12 sec segments

---

## 👨‍💻 Author: @andvsilva

---

## 📜 License

MIT License

---