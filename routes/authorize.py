from flask import Blueprint, render_template, request, jsonify

authorize_bp = Blueprint("authorize", __name__)

# 用户点击 /authorize 时才返回真正内容
@authorize_bp.route("/authorize", methods=["POST"])
def authorize():
    # 可以加逻辑检查，比如验证 headers 或 request.json
    return render_template("test_real.html")