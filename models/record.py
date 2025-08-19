from datetime import datetime
from extensions import db

class LoginRecord(db.Model):
    __tablename__ = 'login_records'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    fingerprint = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String(64))        # 新增
    cookie = db.Column(db.Text)