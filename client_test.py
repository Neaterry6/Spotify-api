import requests

API_URL = "http://localhost:8000"

def test_chat():
    prompt = "Hello AI, how are you today?"
    response = requests.post(f"{https://spotify-api-jn6h.onrender.com}/chat", data={"prompt": prompt})
    if response.ok:
        print("Chat AI Response:", response.json().get("response"))
    else:
        print("Chat AI Error:", response.text)

def test_ocr(image_path):
    with open(image_path, "rb") as img_file:
        files = {"file": img_file}
        response = requests.post(f"{https://spotify-api-jn6h.onrender.com}/ocr", files=files)
    if response.ok:
        print("OCR Extracted Text:", response.json().get("extracted_text"))
    else:
        print("OCR Error:", response.text)

if __name__ == "__main__":
    print("Testing AI chat endpoint:")
    test_chat()
    print("\nTesting OCR endpoint with sample image 'sample.jpg':")
    test_ocr("sample.jpg")