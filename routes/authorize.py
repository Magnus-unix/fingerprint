# routes/authorize.py 或 routes/login.py 内
from flask import Blueprint, request, jsonify, render_template_string, current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/authorize', methods=['POST'])
def authorize():
    data = request.get_json() or {}
    fingerprint = data.get('fingerprint', {})
    # 记录（存 DB 日志）
    current_app.logger.info('[AUTH] fingerprint received from %s', request.remote_addr)

    # 这里可以做简单策略：例如判断 fingerprint 是否有关键字段、频率限制、IP黑名单等
    allowed = True  # 简单放行（你可以改为更严格）
    
    if allowed:
        # 方法 A：直接返回要插入的 HTML（慎用：确保内容安全）
        content_html = """
        <div class="container">
          <h1>The Traveler’s Journey</h1>
          <img id="randomImage" src="" alt="Random scenery">
          <p>...正文内容...</p>
          <a href="https://en.wikipedia.org" target="_blank">Visit Wikipedia 🌐</a>
        </div>
        """
        return jsonify({'allowed': True, 'content': content_html})
    else:
        return jsonify({'allowed': False}), 200
