"""MP Suvidha: Madhya Pradesh Digital Services Portal
Independent Citizen Service Information & Application Portal.
"""
import os
from flask import Flask, jsonify, render_template
from backend.config import Config
from backend.database import init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.service_routes import service_bp
from backend.routes.application_routes import application_bp
from backend.routes.certificate_routes import certificate_bp
from backend.routes.evaluation_routes import evaluation_bp
from backend.routes.feedback_routes import feedback_bp
from backend.routes.announcement_routes import announcement_bp
from backend.routes.admin_routes import admin_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

# Register Modular Route Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(service_bp)
app.register_blueprint(application_bp)
app.register_blueprint(certificate_bp)
app.register_blueprint(evaluation_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(announcement_bp)
app.register_blueprint(admin_bp)

@app.get("/")
def home():
    """Serves the main single-page MP Suvidha web portal."""
    return render_template("index.html")

@app.get("/poster")
def poster():
    """Serves internal presentation information."""
    return render_template("poster.html")

@app.get("/api/health")
def health():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "portal": "MP Suvidha",
        "subtitle": "Madhya Pradesh Digital Services",
        "tagline": "One Portal. Multiple Services.",
        "database": "SQLite 3",
        "version": "3.0.0"
    })

@app.errorhandler(404)
def not_found(_err):
    return jsonify({"error": "Requested resource was not found on this server."}), 404

@app.errorhandler(413)
def payload_too_large(_err):
    return jsonify({"error": "Upload size exceeds the limit. Keep each attached file under 5 MB."}), 413

@app.errorhandler(500)
def server_error(_err):
    return jsonify({"error": "An internal server error occurred. Please try again."}), 500

# Initialize schema and seed data on launch
init_db()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"\n=======================================================")
    print(f" MP SUVIDHA: Madhya Pradesh Digital Services")
    print(f" Server running at: http://{host}:{port}")
    print(f" Press Ctrl+C to stop the local development server.")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=debug_mode)
