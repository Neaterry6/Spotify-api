from fastapi import FastAPI, Query, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from PIL import Image
import pytesseract
import io
import subprocess, os

app = FastAPI()

COOKIES = "cookies.txt"

# Initialize AI chat model/tokenizer once
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

# Download audio from YouTube
@app.get("/play")
def play(song: str = Query(...)):
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

# Lyrics route - fixed to handle multiple subtitle extensions
@app.get("/lyrics")
def lyrics(song: str = Query(...)):
    try:
        search_url = f"ytsearch1:{song} lyrics"
        output_path = "%(title)s.%(ext)s"

        # Download auto subtitles only
        cmd = [
            "yt-dlp", "--cookies", COOKIES, "--write-auto-sub", "--sub-lang", "en",
            "--skip-download", "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)

        # Try to find a subtitle file with common extensions
        subtitle_file = None
        for ext in [".en.vtt", ".en.srt", ".vtt", ".srt"]:
            candidates = [f for f in os.listdir() if f.endswith(ext)]
            if candidates:
                subtitle_file = candidates[0]
                break

        if not subtitle_file:
            return {"lyrics": "No subtitles/lyrics found for this song."}

        # Parse subtitle text (works for .vtt and .srt)
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

        # Clean up downloaded subtitle file
        os.remove(subtitle_file)

        return {"lyrics": lyrics_text}
    except Exception as e:
        return {"lyrics": f"Error: {e}"}

# AI Chat route
@app.post("/chat")
async def chat(prompt: str = Form(...)):
    try:
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output_ids = model.generate(
            input_ids,
            max_length=150,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7
        )
        response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        reply = response[len(prompt):].strip()
        if not reply:
            reply = "Sorry, I couldn't generate a response."
        return {"response": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# OCR route to extract text from uploaded image
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