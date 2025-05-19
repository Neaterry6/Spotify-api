import subprocess

def download_song(query):
    try:
        result = subprocess.run(
            ["spotdl", query],
            capture_output=True,
            text=True
        )
        return {
            "status": "success",
            "output": result.stdout
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        
