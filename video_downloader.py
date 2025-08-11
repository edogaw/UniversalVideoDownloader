#!/usr/bin/env python3
"""
Simple cross-site video downloader GUI using yt-dlp.
Supports YouTube, Facebook, TikTok, X, Reddit and many more sites supported by yt-dlp.

Usage: python video_downloader.py
"""

import threading
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
from yt_dlp.utils import DownloadError

# Helper: build format string based on user choice
def format_for_choice(choice):
    if choice == "Highest (merge best video+audio)":
        # try bestvideo+bestaudio then fallback to best
        return "bestvideo+bestaudio/best"
    if choice == "1080p":
        return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    if choice == "720p":
        return "bestvideo[height<=720]+bestaudio/best[height<=720]"
    if choice == "480p":
        return "bestvideo[height<=480]+bestaudio/best[height<=480]"
    if choice == "Audio only (bestaudio)":
        return "bestaudio"
    return "best"

class App:
    def __init__(self, root):
        self.root = root
        root.title("Video Downloader (yt-dlp)")

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # URL entry
        ttk.Label(frm, text="Video URL:").grid(row=0, column=0, sticky="w")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(frm, textvariable=self.url_var, width=70)
        self.url_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0,8))

        # Save path
        ttk.Label(frm, text="Save folder:").grid(row=2, column=0, sticky="w")
        self.path_var = tk.StringVar(value=os.path.expanduser("~"))
        self.path_entry = ttk.Entry(frm, textvariable=self.path_var, width=50)
        self.path_entry.grid(row=3, column=0, sticky="we")
        ttk.Button(frm, text="Browse...", command=self.browse).grid(row=3, column=1, sticky="w", padx=(6,0))

        # Format/resolution choice
        ttk.Label(frm, text="Quality:").grid(row=4, column=0, sticky="w", pady=(8,0))
        self.choice_var = tk.StringVar(value="Highest (merge best video+audio)")
        choices = ["Highest (merge best video+audio)", "1080p", "720p", "480p", "Audio only (bestaudio)"]
        self.combo = ttk.Combobox(frm, values=choices, textvariable=self.choice_var, state="readonly", width=35)
        self.combo.grid(row=5, column=0, sticky="w", pady=(0,8))

        # Filename template (optional)
        ttk.Label(frm, text="Filename template (optional):").grid(row=6, column=0, sticky="w")
        self.template_var = tk.StringVar(value="%(title)s.%(ext)s")
        self.template_entry = ttk.Entry(frm, textvariable=self.template_var, width=50)
        self.template_entry.grid(row=7, column=0, sticky="we", pady=(0,8))

        # Buttons
        self.download_btn = ttk.Button(frm, text="Download", command=self.start_download)
        self.download_btn.grid(row=8, column=0, sticky="w")

        self.cancel_btn = ttk.Button(frm, text="Quit", command=root.destroy)
        self.cancel_btn.grid(row=8, column=1, sticky="w", padx=(6,0))

        # Progress
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(frm, textvariable=self.status_var)
        self.status_label.grid(row=9, column=0, columnspan=3, sticky="w", pady=(10,0))

        self.progress = ttk.Progressbar(frm, mode="determinate", length=480)
        self.progress.grid(row=10, column=0, columnspan=3, sticky="we", pady=(6,0))

        # Make UI stretch nicely
        for i in range(3):
            frm.columnconfigure(i, weight=1)

        # Internal
        self.ydl = None
        self._downloading = False

    def browse(self):
        d = filedialog.askdirectory(initialdir=self.path_var.get() or os.path.expanduser("~"))
        if d:
            self.path_var.set(d)

    def start_download(self):
        url = self.url_var.get().strip()
        folder = self.path_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste a video URL.")
            return
        if not folder:
            messagebox.showwarning("Missing folder", "Please choose a save folder.")
            return
        # disable UI
        self.download_btn.config(state="disabled")
        self._downloading = True
        self.status_var.set("Queued...")
        thread = threading.Thread(target=self._download_thread, args=(url, folder), daemon=True)
        thread.start()

    def _progress_hook(self, d):
        # yt-dlp sends status updates
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            speed = d.get("speed") or 0
            eta = d.get("eta") or 0
            if total:
                pct = int(downloaded * 100 / total)
                self.progress['value'] = pct
                self.status_var.set(f"Downloading... {pct}% — {d.get('_eta_str','')}  ({d.get('_speed_str','')})")
            else:
                # indeterminate
                self.progress.config(mode="indeterminate")
                try:
                    self.progress.start(10)
                except Exception:
                    pass
                self.status_var.set(f"Downloading... {d.get('_eta_str','')}")
        elif status == "finished":
            # stop progress
            try:
                self.progress.stop()
            except Exception:
                pass
            self.progress.config(mode="determinate")
            self.progress['value'] = 100
            self.status_var.set("Merging/processing final file...")
        elif status == "error":
            self.status_var.set("Error during download.")

    def _download_thread(self, url, folder):
        choice = self.choice_var.get()
        fmt = format_for_choice(choice)
        template = self.template_var.get().strip() or "%(title)s.%(ext)s"
        # Basic options:
        ydl_opts = {
            "format": fmt,
            "outtmpl": os.path.join(folder, template),
            "noprogress": False,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            # use ffmpeg if needed to merge; requires ffmpeg installed in PATH for some merges
            "postprocessors": [{
                "key": "FFmpegMetadata"
            }],
            # write info json for debugging if needed
            # "writethumbnail": True,
        }

        # If audio only, convert to mp3 (optional). We'll avoid forcing conversions to keep it simple.
        if choice == "Audio only (bestaudio)":
            # optional: add postprocessor to extract audio (mp3)
            ydl_opts["postprocessors"].append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            })
            # adjust output ext
            # note: yt-dlp will change ext to mp3 automatically after postprocessing

        # Create a new YDL object each download to avoid internal state issues
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # show starting status in GUI thread
                self._set_status_mainthread("Starting download...")
                ydl.download([url])
            self._set_status_mainthread("Done — download completed.")
            messagebox.showinfo("Download complete", f"Download finished and saved to:\n{folder}")
        except DownloadError as de:
            self._set_status_mainthread("Download error.")
            messagebox.showerror("Download error", str(de))
        except Exception as e:
            # Generic catch
            self._set_status_mainthread("Error.")
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            # re-enable UI
            self._set_status_mainthread("Ready")
            self._set_mainthread(lambda: self.download_btn.config(state="normal"))
            self._downloading = False
            self._set_mainthread(lambda: self.progress.config(mode="determinate"))
            self._set_mainthread(lambda: self.progress.stop())

    # helpers to update UI from background thread safely
    def _set_status_mainthread(self, text):
        self._set_mainthread(lambda: self.status_var.set(text))

    def _set_mainthread(self, fn):
        try:
            self.root.after(0, fn)
        except Exception:
            pass

def main():
    root = tk.Tk()
    app = App(root)
    root.geometry("640x300")
    root.mainloop()

if __name__ == "__main__":
    main()
