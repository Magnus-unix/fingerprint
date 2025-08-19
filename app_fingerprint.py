from flask import Flask
from flask_cors import CORS
from config import *
from fingerprint.api import fingerprint_bp
from extensions import db

def create_fingerprint_app():
    app = Flask(__name__)
    app.config.from_object('config')  # ✅ 确保加载 config.py
    db.init_app(app)

    # ✅ 启用跨域，并允许携带 Cookie
    CORS(app, supports_credentials=True)

    app.register_blueprint(fingerprint_bp)
    return app

if __name__ == '__main__':
    app = create_fingerprint_app()
    app.run(host='0.0.0.0', port=8081, debug=True)
