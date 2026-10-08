import os
from flask import Flask, render_template

# ---------------------------------------------------------------------------
# REP Counter AI — Lightweight Web Server
# All real-time pose tracking and rep counting run 100% in the user's browser
# via Google MediaPipe Tasks Vision. Server requires < 40MB RAM on Render.
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route('/')
def index():
    """Serve REP Counter AI live workout application."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Serve workout dashboard."""
    sample_workouts = [
        {'date': 'Today', 'exercise': 'Bicep Curls', 'reps': 30, 'duration': '04:12', 'score': '98%'},
        {'date': 'Today', 'exercise': 'Squats', 'reps': 25, 'duration': '03:45', 'score': '95%'},
        {'date': 'Yesterday', 'exercise': 'Push-Ups', 'reps': 20, 'duration': '02:30', 'score': '92%'},
    ]
    return render_template(
        'dashboard.html',
        total_workouts=14,
        total_exercises=7,
        weekly_workouts=5,
        streak_days=4,
        recent_workouts=sample_workouts
    )


@app.route('/profile')
def profile():
    """Serve user profile."""
    user = {
        'name': 'Athlete',
        'title': 'Fitness Enthusiast',
        'initials': 'RC',
        'joined': 'October 2026'
    }
    stats = {
        'total_workouts': 14,
        'total_reps': 420,
        'total_minutes': 68,
        'streak': 4,
        'avg_form_score': 94
    }
    settings = {
        'notifications': True,
        'dark_mode': True,
        'sounds': True,
        'units': 'metric'
    }
    favorites = [
        {'name': 'Bicep Curls', 'count': 45},
        {'name': 'Squats', 'count': 38},
        {'name': 'Push-Ups', 'count': 28}
    ]
    return render_template(
        'profile.html',
        user=user,
        stats=stats,
        favorites=favorites,
        settings=settings
    )


@app.route('/health')
def health():
    """Health-check endpoint for Render / AWS monitoring."""
    return {'status': 'ok', 'app': 'REP Counter AI'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)