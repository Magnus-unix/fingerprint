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

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    fingerprint = data.get('fingerprint')  # ✅ 只记录ID

    user = User.query.filter_by(username=username).first()

    success = user and user.password == password
    record = LoginRecord(
        username=username,
        fingerprint=fingerprint,  # ✅ 简化，只存 fingerprint
        timestamp=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'success': success,
        'message': '登录成功' if success else '用户名或密码错误'
    })
    
@login_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        fingerprint_raw = request.form.get('fingerprint', '{}')

        try:
            fingerprint = json.loads(fingerprint_raw)
        except json.JSONDecodeError:
            fingerprint = {}

        # 检查是否已存在
        if User.query.filter_by(username=username).first():
            error = '用户名已存在'
        else:
            new_user = User(
                username=username,
                password=password,  # 可在后续加密码哈希
                fingerprint=json.dumps(fingerprint, ensure_ascii=False)
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login.login'))  # 注册成功跳转登录页

    return render_template('register.html', error=error)

@login_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@login_bp.route('/test')
def test_page():
    return render_template('test.html')
