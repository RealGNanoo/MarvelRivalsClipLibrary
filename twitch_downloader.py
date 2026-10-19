import os
import re
from typing import Optional
import yt_dlp


def sanitize_filename(name: str) -> str:
    """Removes filesystem-incompatible characters from video titles."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def download_clip(
    slug: str,
    title: str,
    thumbnail_url: str = "",
    download_dir: str = "downloads",
) -> Optional[str]:
    """Downloads a Twitch clip directly using yt-dlp."""
    os.makedirs(download_dir, exist_ok=True)
    safe_title = sanitize_filename(title) or "clip"
    out_template = os.path.join(download_dir, f"{safe_title}_{slug}.%(ext)s")
    clip_url = f"https://clips.twitch.tv/{slug}"

    ydl_opts = {
        "outtmpl": out_template,
        "format": "best",
        "quiet": False,
        "no_warnings": True,
    }

    try:
        print(f"[+] Downloading via yt-dlp: {safe_title} ({slug})...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clip_url, download=True)
            saved_file = ydl.prepare_filename(info)
            # Handle potential container extension adjustments
            if not os.path.exists(saved_file):
                base_name = os.path.splitext(saved_file)[0]
                for ext in [".mp4", ".mkv", ".webm"]:
                    if os.path.exists(base_name + ext):
                        saved_file = base_name + ext
                        break

            print(f"[✓] Successfully downloaded: {saved_file}")
            return saved_file
    except Exception as e:
        print(f"[-] Failed to download clip {slug}: {e}")
        return None