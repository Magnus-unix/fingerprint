from flask import Blueprint, request, jsonify
from models.record import LoginRecord
from extensions import db
from datetime import datetime
import json

fingerprint_bp = Blueprint('fingerprint', __name__)

@fingerprint_bp.route('/fingerprint', methods=['POST'])
def collect_fingerprint():
    data = request.get_json()
    print("收到的数据：", data)
    username = data.get('username')
    fingerprint = data.get('fingerprint', {})

    if not username:
        return jsonify({'success': False, 'message': '用户名缺失'}), 400

    # 获取用户真实 IP（优先 X-Forwarded-For，否则 remote_addr）
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # 获取 cookie（如果是跨域 fetch，要确认 credentials: 'include'）
    cookie = request.headers.get("Cookie", "")

    record = LoginRecord(
        username=username,
        fingerprint=json.dumps(fingerprint, ensure_ascii=False),
        ip=ip,
        cookie=cookie,
        timestamp=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'success': True})

