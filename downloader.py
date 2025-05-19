import subprocess
import os

def download_song(song_name):
    try:
        # Path to your cookies file
        cookies_path = os.path.join(os.getcwd(), 'cookies.txt')

        # Build yt-dlp command
        cmd = [
            "yt-dlp",
            f"ytsearch1:{song_name}",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", f"{song_name}.%(ext)s",
            "--cookies", cookies_path
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            return f"{song_name}.mp3"
        else:
            return f"Error downloading song: {result.stderr}"

    except Exception as e:
        return f"Error downloading song: {str(e)}"
