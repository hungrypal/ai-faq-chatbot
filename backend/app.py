# ============================================================
#  app.py — Flask Application Entry Point
#  Run: python app.py
# ============================================================

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Import route blueprints
from routes.chat  import chat_bp
from routes.admin import admin_bp

# ── Create Flask App ─────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow frontend (HTML file) to call the API

# ── Register Blueprints (Route Groups) ───────────────────
app.register_blueprint(chat_bp,  url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# ── Health Check Route ────────────────────────────────────
@app.route('/')
def index():
    return {'status': 'ShopMind AI backend is running ✅', 'version': '1.0'}

# ── Run Server ────────────────────────────────────────────
if __name__ == '__main__':
    port  = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    print(f"\n🚀 ShopMind AI running at http://localhost:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
