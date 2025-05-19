from fastapi import FastAPI, Query, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import pytesseract
import io
import subprocess
import os
import requests

app = FastAPI()

COOKIES = "cookies.txt"
KAIZ_API_KEY = "423c0305-cf71-48dc-b57f-693399ce53d1"
KAIZ_API_URL = "https://kaiz-apis.gleeze.com/api/gpt-3.5"

# Helper to clean old media files after request (optional)
def cleanup_files(extensions=[".mp3", ".mp4", ".vtt", ".srt"]):
    for f in os.listdir():
        if any(f.endswith(ext) for ext in extensions):
            try:
                os.remove(f)
            except:
                pass

# Download audio from YouTube
@app.get("/play")
def play(song: str = Query(...)):
    cleanup_files()
    try:
        search_url = f"ytsearch1:{song}"
        output_path = "audio.%(ext)s"
        cmd = [
            "yt-dlp", "--cookies", COOKIES, "-x", "--audio-format", "mp3",
            "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)
        mp3_file = next((f for f in os.listdir() if f.endswith(".mp3")), None)
        if mp3_file:
            return FileResponse(mp3_file, media_type="audio/mpeg", filename=mp3_file)
        return {"result": "Audio download failed."}
    except Exception as e:
        return {"result": f"Error: {e}"}

# Download video from YouTube
@app.get("/video")
def video(search: str = Query(...)):
    cleanup_files()
    try:
        search_url = f"ytsearch1:{search}"
        output_path = "video.%(ext)s"
        cmd = [
            "yt-dlp", "--cookies", COOKIES, "-f", "mp4", "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)
        video_file = next((f for f in os.listdir() if f.endswith(".mp4")), None)
        if video_file:
            return FileResponse(video_file, media_type="video/mp4", filename=video_file)
        return {"result": "Video download failed."}
    except Exception as e:
        return {"result": f"Error: {e}"}

# Lyrics fetching
@app.get("/lyrics")
def lyrics(song: str = Query(...)):
    cleanup_files()
    try:
        search_url = f"ytsearch1:{song} lyrics"
        output_path = "%(title)s.%(ext)s"

        cmd = [
            "yt-dlp", "--cookies", COOKIES, "--write-auto-sub", "--sub-lang", "en",
            "--skip-download", "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)

        subtitle_file = None
        for ext in [".en.vtt", ".en.srt", ".vtt", ".srt"]:
            candidates = [f for f in os.listdir() if f.endswith(ext)]
            if candidates:
                subtitle_file = candidates[0]
                break

        if not subtitle_file:
            return {"lyrics": "No subtitles/lyrics found for this song."}

        def parse_subtitles(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            text = ""
            for line in lines:
                line = line.strip()
                if line == "" or line.startswith("WEBVTT") or line[0].isdigit() or "-->" in line:
                    continue
                text += line + " "
            return text.strip()

        lyrics_text = parse_subtitles(subtitle_file)
        os.remove(subtitle_file)

        return {"lyrics": lyrics_text}
    except Exception as e:
        return {"lyrics": f"Error: {e}"}

# OCR to extract text from uploaded image
@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image).strip()
        if not text:
            text = "No text found in the image."
        return {"extracted_text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Chatbot using Kaiz API GPT-3.5 with image generation
@app.post("/chat")
async def chat(prompt: str = Form(...)):
    try:
        params = {
            "q": prompt,
            "apikey": KAIZ_API_KEY
        }
        response = requests.get(KAIZ_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            text_response = data.get("response") or ""
            image_url = data.get("image")  # If API returns an image URL

            result = {"response": text_response}
            if image_url:
                result["image_url"] = image_url

            return result
        else:
            return JSONResponse(status_code=500, content={"error": "AI API request failed."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
