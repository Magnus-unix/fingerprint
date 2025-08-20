# models/record.py
from extensions import db

class LoginRecord(db.Model):
    __tablename__ = 'login_records'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    fingerprint = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(512), nullable=True)   # 👈 新增 URL 字段
    timestamp = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(45), nullable=True)
    cookie = db.Column(db.String(512), nullable=True)
