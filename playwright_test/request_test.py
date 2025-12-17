# 
import requests
import urllib3

# 1. 屏蔽烦人的 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 配置
LOGIN_URL = "https://skyeker.top/login"
TARGET_URL = "https://magnus-unix.github.io/fingerprint/index.html" # 随便填一个验证用的

payload = {
    "username": "admin",
    "password": "123456"
}

headers = {
    # 尽可能伪装得像浏览器
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://magnus-unix.github.io/",
    "Origin": "https://magnus-unix.github.io",
    "Content-Type": "application/json"
}

session = requests.Session()

try:
    print(f"正在尝试登录 (已关闭SSL验证): {LOGIN_URL} ...")
    
    # 重点修改：
    # 1. json=payload (因为后端是 request.get_json())
    # 2. verify=False (关键！不验证证书，直接硬连)
    response = session.post(LOGIN_URL, json=payload, headers=headers, verify=False)
    
    print(f"状态码: {response.status_code}")
    print(f"返回内容: {response.text}")

    if response.status_code == 200:
        print("✅ 登录接口请求成功！")
    else:
        print("❌ 接口返回错误。")

except Exception as e:
    print(f"还是报错了: {e}")