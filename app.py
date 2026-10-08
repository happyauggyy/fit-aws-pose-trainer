import os
# Suppress TensorFlow/XLA noise before any mediapipe import
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import base64
import numpy as np
import cv2

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# MediaPipe Pose – initialised once at process startup.
# mediapipe==0.10.9 ships a cp311-manylinux wheel that works on Render.
# mp.solutions.pose is the stable high-level API for this version.
# ---------------------------------------------------------------------------
try:
    import mediapipe as mp
    _mp_pose = mp.solutions.pose
    pose = _mp_pose.Pose(
        static_image_mode=True,
        model_complexity=0,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3,
    )
    print("[STARTUP] MediaPipe Pose initialised successfully.", flush=True)
except Exception as _e:
    print(f"[STARTUP ERROR] MediaPipe init failed: {_e}", flush=True)
    pose = None

# ---------------------------------------------------------------------------
# Global rep state (survives across requests in a single gunicorn worker)
# ---------------------------------------------------------------------------
global_rep_counter = 0
global_exercise_stage = "down"


def calculate_angle(a, b, c):
    """Return the joint angle (degrees) formed by three MediaPipe landmarks."""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    radians = (
        np.arctan2(c[1] - b[1], c[0] - b[0])
        - np.arctan2(a[1] - b[1], a[0] - b[0])
    )
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_frame', methods=['POST'])
def process_frame():
    global global_rep_counter, global_exercise_stage

    payload = request.get_json(silent=True) or {}
    image_data = payload.get('image', '')

    # Strip the data-URL header if present (e.g. "data:image/jpeg;base64,...")
    if ',' in image_data:
        image_data = image_data.split(',', 1)[1]

    if not image_data:
        return jsonify({
            'reps': global_rep_counter,
            'stage': global_exercise_stage,
            'success': False,
        }), 200

    try:
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            return jsonify({
                'reps': global_rep_counter,
                'stage': global_exercise_stage,
                'success': False,
            }), 200

        if pose is None:
            return jsonify({
                'reps': global_rep_counter,
                'stage': global_exercise_stage,
                'error': 'pose detector unavailable',
                'success': False,
            }), 200

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Prefer right arm; fall back to left if right elbow not visible
            shoulder = landmarks[12]
            elbow    = landmarks[14]
            wrist    = landmarks[16]
            if elbow.visibility < 0.5:
                shoulder = landmarks[11]
                elbow    = landmarks[13]
                wrist    = landmarks[15]

            angle = calculate_angle(shoulder, elbow, wrist)

            if angle > 150:
                global_exercise_stage = "down"
            elif angle < 50 and global_exercise_stage == "down":
                global_exercise_stage = "up"
                global_rep_counter += 1
                print(
                    f"[REP] >>> REP COUNTED! Total: {global_rep_counter} <<<",
                    flush=True,
                )

            print(
                f"[REP] Angle: {int(angle)}° | Stage: {global_exercise_stage}"
                f" | Total: {global_rep_counter}",
                flush=True,
            )
            return jsonify({
                'reps':  global_rep_counter,
                'angle': int(angle),
                'stage': global_exercise_stage,
                'success': True,
            }), 200

        else:
            return jsonify({
                'reps':  global_rep_counter,
                'stage': global_exercise_stage,
                'success': False,
            }), 200

    except Exception as e:
        print(f"[ERROR] process_frame: {e}", flush=True)
        return jsonify({
            'reps':  global_rep_counter,
            'stage': global_exercise_stage,
            'error': str(e),
            'success': False,
        }), 200


@app.route('/reset', methods=['POST'])
def reset():
    global global_rep_counter, global_exercise_stage
    global_rep_counter = 0
    global_exercise_stage = "down"
    return jsonify({'reps': 0, 'stage': 'down', 'success': True}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)