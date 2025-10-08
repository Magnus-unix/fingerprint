from flask import Blueprint, request, render_template, jsonify
from datetime import datetime

authorize_bp = Blueprint('authorize', __name__)

# ✅ 授权接口
@authorize_bp.route('/authorize', methods=['POST'])
def authorize():
    data = request.get_json(silent=True) or {}
    ip = request.remote_addr
    js_executed = data.get('js_executed', False)
    timestamp = data.get('timestamp', None)

    # ✅ 打印日志（记录时间戳和 IP）
    print(f"[AUTHORIZE] JS executed={js_executed}, timestamp={timestamp}, from IP={ip}")

    # ✅ 如果 JS 执行了，返回真实内容
    if js_executed:
        return render_template('real_test.html')

    # 🚫 否则返回提示（比如非 JS 环境访问）
    return jsonify({
        "error": "JavaScript not detected",
        "message": "Please enable JavaScript to view this page"
    }), 400
