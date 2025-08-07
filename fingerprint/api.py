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

    # ✅ 将 fingerprint 原样存入数据库
    record = LoginRecord(
        username=username,
        fingerprint=json.dumps(fingerprint, ensure_ascii=False),  # 原始 JSON 字符串化
        timestamp=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'success': True})
