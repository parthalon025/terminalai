#!/usr/bin/env python3
"""
YouTube Video Downloader
Downloads YouTube videos to MP4 format using yt-dlp.

Usage:
    python download_youtube.py <video_url> [output_dir]

Examples:
    python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
    python download_youtube.py https://youtu.be/dQw4w9WgXcQ ./my_videos
"""

import subprocess
import sys
import os
from pathlib import Path


def download_video(url: str, output_dir: str = "./downloads") -> bool:
    """
    Download a YouTube video as MP4.

    Args:
        url: YouTube video URL
        output_dir: Directory to save the video (default: ./downloads)

    Returns:
        True if successful, False otherwise
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # yt-dlp command to download best video+audio merged to MP4
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(output_path / "%(title)s.%(ext)s"),
        "--no-playlist",  # Download single video, not playlist
        "--progress",
        url
    ]

    print(f"Downloading video to: {output_path.absolute()}")
    print(f"URL: {url}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 50)
        print("Download complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        return False
    except FileNotFoundError:
        print("Error: yt-dlp not found. Install it with: pip install yt-dlp")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./downloads"

    success = download_video(url, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
