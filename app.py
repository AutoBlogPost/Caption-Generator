
# Install necessary libraries
!pip install yt-dlp ffmpeg whisper flask

import os
import whisper
import yt_dlp
import ffmpeg
from flask import Flask, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

# Function to download audio from YouTube
def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return ydl.prepare_filename(info_dict).replace('.webm', '.mp3')
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

@app.route('/generate_captions', methods=['POST'])
def generate_captions():
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        print("Error: No video URL provided.")
        return jsonify({"error": "No video URL provided"}), 400

    # Step 1: Download the audio file from YouTube
    audio_file = download_audio(video_url)
    if not audio_file:
        print("Error: Failed to download audio.")
        return jsonify({"error": "Failed to download audio"}), 500

    print(f"Audio file downloaded successfully: {audio_file}")

    # Step 2: Transcribe audio using Whisper
    try:
        model = whisper.load_model("base")
        print("Whisper model loaded.")
        result = model.transcribe(audio_file)
        transcription = result.get("text", "No transcription available")
        print(f"Transcription: {transcription}")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"error": "Transcription failed"}), 500

    # Step 3: Return the transcription as a JSON response
    return jsonify({"transcription": transcription})

# Run the Flask app on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
