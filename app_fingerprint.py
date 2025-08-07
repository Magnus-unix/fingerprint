from flask import Flask
from flask_cors import CORS  # ✅ 导入 CORS
from config import *
from fingerprint.api import fingerprint_bp
from extensions import db

def create_fingerprint_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    db.init_app(app)

    CORS(app)  # ✅ 在这里启用跨域支持

    app.register_blueprint(fingerprint_bp)
    return app

if __name__ == '__main__':
    app = create_fingerprint_app()
    app.run(host='0.0.0.0', port=8081, debug=True)
