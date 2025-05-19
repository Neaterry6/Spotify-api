def get_lyrics(track):
    # Dummy implementation for example
    # Replace with real lyrics fetch code or API
    dummy_lyrics = {
        "Imagine": "Imagine all the people...",
        "Hello": "Hello, it's me..."
    }
    return dummy_lyrics.get(track, "")

def download_song(track):
    # Dummy implementation for example
    # Replace with real download logic or API
    return {
        "message": f"Song '{track}' downloaded successfully.",
        "download_link": f"https://example.com/downloads/{track.replace(' ', '_')}.mp3"
    }
