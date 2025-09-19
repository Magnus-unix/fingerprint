from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from models.user import User
from models.record import LoginRecord
from extensions import db
import json
from datetime import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route('/')
def index():
    return redirect(url_for('login.login'))  # 注意这里 login.login 是蓝图+视图名

from flask import make_response

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    fingerprint = data.get('fingerprint')  # 只记录指纹

    user = User.query.filter_by(username=username).first()
    success = user and user.password == password

    # 记录登录信息
    record = LoginRecord(
        username=username,
        fingerprint=fingerprint,
        timestamp=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()

    # 创建响应对象
    resp = make_response(jsonify({
        'success': success,
        'message': '登录成功' if success else '用户名或密码错误'
    }))

    # 登录成功时设置 cookie，有效期 30 天
    if success:
        cookie_value = f"{username}:{password}"  
        resp.set_cookie(
            key='user_cookie',
            value=cookie_value,
            max_age=30*24*60*60,
            secure=True,
            httponly=True,
            samesite='None'
        )
    return resp

@login_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@login_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # 查重
    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "此用户名已被注册"}), 200

    # 保存
    new_user = User(username=username, password=password, fingerprint="{}")
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "注册成功"}), 200

@login_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@login_bp.route('/test')
def test_page():
    return render_template('test.html')
