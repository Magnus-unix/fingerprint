from flask import Blueprint, request, jsonify
from models.record import LoginRecord
from extensions import db
from datetime import datetime
import json

fingerprint_bp = Blueprint('fingerprint', __name__)

@fingerprint_bp.route('/fingerprint', methods=['POST'])
def collect_fingerprint():
    data = request.get_json()
    username = data.get('username')
    fingerprint = data.get('fingerprint', {})
    url = data.get('url', '')
    ip = data.get('ip', '')       # 👈 从前端传来的真实 IP
    cookie = data.get('cookie', '')  # 👈 从前端传来的 cookie

    if not username:
        return jsonify({'success': False, 'message': '用户名缺失'}), 400

    record = LoginRecord(
        username=username,
        fingerprint=json.dumps(fingerprint, ensure_ascii=False),
        url=url,
        ip=ip,
        cookie=cookie,
        timestamp=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'success': True})

