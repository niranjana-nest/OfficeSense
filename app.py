
from flask import Flask, render_template, request, url_for
from video_processor import process_video, convert_to_mp4
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def index():

    results = None
    original_url = None
    video_url = None
    error = None

    if request.method == "POST":

        uploaded_file = request.files.get("video")

        if not uploaded_file or not uploaded_file.filename:
            error = "Please select a video."

        else:
            extension = os.path.splitext(
                uploaded_file.filename
            )[1].lower()

            if extension not in [".mp4", ".avi", ".mov"]:
                error = "Unsupported video format."

            else:
                filename = uuid.uuid4().hex

                input_path = os.path.join(
                    UPLOAD_FOLDER,
                    filename + extension
                )

                original_mp4 = os.path.join(
                    UPLOAD_FOLDER,
                    filename + "_original.mp4"
                )

                output_path = os.path.join(
                    OUTPUT_FOLDER,
                    filename + "_annotated.mp4"
                )

                try:
                    uploaded_file.save(input_path)

                    # Convert original for browser playback
                    convert_to_mp4(
                        input_path,
                        original_mp4
                    )

                    # Run YOLO
                    results = process_video(
                        input_path,
                        output_path
                    )

                    original_url = url_for(
                        "static",
                        filename="uploads/" + filename + "_original.mp4"
                    )

                    video_url = url_for(
                        "static",
                        filename="outputs/" + filename + "_annotated.mp4"
                    )

                except Exception as e:
                    error = f"Processing failed: {e}"

                finally:
                    if os.path.exists(input_path):
                        os.remove(input_path)

    return render_template(
        "index.html",
        results=results,
        original_url=original_url,
        video_url=video_url,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
