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
    url = data.get('url', '')   # 👈 单独取 URL

    if not username:
        return jsonify({'success': False, 'message': '用户名缺失'}), 400

    record = LoginRecord(
        username=username,
        fingerprint=json.dumps(fingerprint, ensure_ascii=False),
        url=url,  # ✅ 保存到独立字段
        timestamp=datetime.utcnow(),
        ip=request.remote_addr,
        cookie=request.cookies.get('session', '')
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'success': True})
