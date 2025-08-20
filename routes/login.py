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

@login_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@login_bp.route('/test')
def test_page():
    return render_template('test.html')
