import os
from flask import Flask, render_template

# ---------------------------------------------------------------------------
# Render is now a LIGHTWEIGHT web server only.
# All pose detection runs in the user's browser via MediaPipe Tasks Vision JS.
# This file imports ONLY Flask — no MediaPipe, OpenCV, NumPy, or cv2.
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the single-page bicep-curl trainer."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health-check endpoint (used by Render uptime monitoring)."""
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)