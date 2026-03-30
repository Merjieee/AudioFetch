from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import re

app = Flask(__name__)

DOWNLOADS = "downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

def clean_filename(name):
    return re.sub(r'[\\/:*?"<>|]', "_", name)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        video_url = data.get("url")

        if not video_url:
            return jsonify({"status": "error", "message": "No URL provided"}), 400

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DOWNLOADS, "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title", "audio")
            filename = clean_filename(title) + ".mp3"

        return jsonify({
            "status": "success",
            "file": filename,
            "title": title
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/get-file/<filename>")
def get_file(filename):
    file_path = os.path.join(DOWNLOADS, filename)

    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="audio/mpeg"
        )

    return jsonify({"status": "error", "message": "File not found"}), 404