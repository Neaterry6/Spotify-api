import yt_dlp
import os
import asyncio

async def download_song(song_name: str) -> str:
    filename = f"{song_name}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Run youtube-dl synchronously in a thread to not block event loop
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f"ytsearch1:{song_name}"]))

    if not os.path.exists(filename):
        raise Exception("Download failed.")
    return filename
