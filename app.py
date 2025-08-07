from flask import Flask
from config import *
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    
    db.init_app(app)

    # 注册蓝图和模型（注意：模型导入要放在 init_app 之后）
    from routes.login import login_bp
    app.register_blueprint(login_bp)

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)