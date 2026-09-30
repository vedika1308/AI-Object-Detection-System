from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from collections import Counter
import os
import cv2

app = Flask(__name__)

# -----------------------------
# FOLDERS
# -----------------------------

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = os.path.join("static", "results")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------
# LOAD YOLO MODEL
# -----------------------------

model = YOLO("yolo11n.pt")


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# UPLOAD AND DETECT
# -----------------------------

@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image uploaded."
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "No image selected."
        }), 400

    # Secure filename
    filename = secure_filename(file.filename)

    upload_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(upload_path)

    # -----------------------------
    # YOLO DETECTION
    # -----------------------------

    results = model.predict(
        source=upload_path,
        conf=0.25,
        verbose=True
    )

    result = results[0]

    # -----------------------------
    # CREATE ANNOTATED IMAGE
    # -----------------------------

    annotated_image = result.plot()

    result_filename = "detected_" + filename

    result_path = os.path.join(
        RESULT_FOLDER,
        result_filename
    )

    cv2.imwrite(
        result_path,
        annotated_image
    )

    # -----------------------------
    # COUNT OBJECTS
    # -----------------------------

    object_counter = Counter()

    if result.boxes is not None:

        class_ids = result.boxes.cls.tolist()

        for class_id in class_ids:

            class_id = int(class_id)

            object_name = model.names[class_id]

            object_counter[object_name] += 1

    # -----------------------------
    # CREATE OBJECT LIST
    # -----------------------------

    objects = []

    for name, count in object_counter.items():

        objects.append({
            "name": name,
            "count": count
        })

    total_objects = sum(
        object_counter.values()
    )

    # -----------------------------
    # SEND RESPONSE
    # -----------------------------

    return jsonify({
        "success": True,
        "result_url": "/static/results/" + result_filename,
        "objects": objects,
        "total": total_objects
    })


# -----------------------------
# OBJECT COUNTS
# -----------------------------

@app.route("/counts")
def counts():

    return jsonify({
        "status": "ready"
    })


# -----------------------------
# RUN FLASK
# -----------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )