# app.py
from flask import Flask
from config import *
from extensions import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # ✅ 确保加载 config.py

    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "https://magnus-unix.github.io"}}, supports_credentials=True)

    # 注册蓝图
    from routes.login import login_bp
    from routes.authorize import auth_bp   # ✅ 新增的蓝图
    app.register_blueprint(login_bp)
    app.register_blueprint(auth_bp)        # ✅ 注册 authorize

    # ✅ 只在数据库为空时初始化，而不是每次都 drop_all
    with app.app_context():
        db.create_all()  

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)

