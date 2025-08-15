# README.md
mysql -u root -p
USE flaskdb;

-- 查看所有记录
SELECT id, username, timestamp, fingerprint FROM login_records;
SELECT id, username, timestamp, LEFT(fingerprint, 100) AS fingerprint_preview FROM login_records ORDER BY id DESC LIMIT 10;