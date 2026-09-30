from flask import Flask, render_template, Response, jsonify, request
from ultralytics import YOLO
import cv2
from collections import Counter
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO("yolo11n.pt")

# Webcam
camera = cv2.VideoCapture(0)

latest_counts = {}


def generate_frames():
    global latest_counts

    while True:
        success, frame = camera.read()

        if not success:
            break

        results = model(frame, verbose=False)

        annotated_frame = results[0].plot()

        names = results[0].names
        detected_classes = results[0].boxes.cls.tolist()

        object_names = [
            names[int(class_id)]
            for class_id in detected_classes
        ]

        latest_counts = dict(Counter(object_names))

        success, buffer = cv2.imencode(
            ".jpg",
            annotated_frame
        )

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/counts")
def counts():
    return jsonify(latest_counts)


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return "No file selected"

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    # Save uploaded file
    input_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(input_path)

    # Check if uploaded file is an image
    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    ]

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension in image_extensions:

        # Run YOLO on image
        results = model(input_path)

        # Save detected image
        result_filename = "detected_" + file.filename

        result_path = os.path.join(
            app.config["RESULT_FOLDER"],
            result_filename
        )

        results[0].save(filename=result_path)

        return render_template(
            "index.html",
            result_image="/results/" + result_filename,
            message="Image detected successfully!"
        )

    return "File uploaded successfully. Video detection will be added next."


@app.route("/results/<filename>")
def result_file(filename):

    from flask import send_from_directory

    return send_from_directory(
        app.config["RESULT_FOLDER"],
        filename
    )


if __name__ == "__main__":
    app.run(debug=True)