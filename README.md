# Universal Video Downloader

A cross-platform, full-resolution video downloader with a simple GUI.  
Supports **YouTube**, **Facebook**, **TikTok**, **X (Twitter)**, **Reddit**, and many other sites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Paste a video link, choose your save folder, pick a resolution, and download — all in one click.

---

## ✨ Features
- ✅ Supports multiple platforms — any site `yt-dlp` can handle.
- ✅ Full resolution (up to 4K+ depending on source).
- ✅ Audio-only mode.
- ✅ Choose save location.
- ✅ Progress bar + ETA in GUI.
- ✅ No command-line knowledge needed.

---

## 📦 Installation

### 1. Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/Universal-Video-Downloader.git
cd Universal-Video-Downloader
````

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

*(Or manually: `pip install yt-dlp tqdm`)*

### 3. Install ffmpeg

`yt-dlp` requires `ffmpeg` for merging video and audio.

#### Windows

1. Download the **release full build** from: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Extract it to `C:\ffmpeg`.
3. Add `C:\ffmpeg\bin` to your PATH
   *(or place `ffmpeg.exe` in the same folder as this script)*.

#### macOS

```bash
brew install ffmpeg
```

#### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 🚀 Usage

```bash
python video_downloader.py
```

1. Paste your video link into the **Video URL** field.
2. Choose your save folder.
3. Select desired resolution/format.
4. Click **Download**.

---

## 📷 Screenshots

*(Add screenshots here once you have them)*

---

## ⚠ Legal Notice

This tool is for **personal use only**.
Do **not** use it to download copyrighted content you do not own or have permission for.
The author is not responsible for any misuse of this software.

Do you also want me to make a **`requirements.txt`** so people can just install dependencies in one command? That will make the repo plug-and-play.
