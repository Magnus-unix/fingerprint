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
    app.register_blueprint(login_bp)

    # ✅ 只在数据库为空时初始化，而不是每次都 drop_all
    with app.app_context():
        db.create_all()  # 如果表不存在会自动创建，不会覆盖已有数据

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
