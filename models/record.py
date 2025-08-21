# models/record.py
from extensions import db
from sqlalchemy.dialects.mysql import LONGTEXT

class LoginRecord(db.Model):
    __tablename__ = 'login_records'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    fingerprint = db.Column(LONGTEXT, nullable=False)   # ✅ 改成 LONGTEXT
    url = db.Column(db.String(1024), nullable=True)     # 建议再放大点
    timestamp = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(45), nullable=True)
    cookie = db.Column(db.Text, nullable=True)          # 改成 Text 以防太长

