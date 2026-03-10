from selenium_stealth import stealth
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By

# ========== 1. 浏览器配置 ==========
options = uc.ChromeOptions()
options.headless = False
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(
    options=options,
    version_main=144,
    use_subprocess=True
)

# ========== 2. Stealth 伪装 ==========
stealth(
   driver,
   languages=["en-US", "en"],
   vendor="Google Inc.",
   platform="MacIntel",
   webgl_vendor="Intel Inc.",
   renderer="Intel Iris OpenGL",
   fix_hairline=True,
)

# ========== 3. 打开你的登录页 ==========
url = "https://magnus-unix.github.io/fingerprint/login.html"
driver.get(url)
time.sleep(2)

# ========== 4. 输入账号密码并登录 ==========
try:
    driver.find_element(By.ID, "username").send_keys("test")
    time.sleep(0.8)

    driver.find_element(By.ID, "password").send_keys("test")
    time.sleep(0.8)

    driver.find_element(By.ID, "loginButton").click()
    print("👉 已点击登录按钮")

except Exception as e:
    print("❌ 登录操作失败：", e)

time.sleep(3)

# ========== 5. 你的指纹检测（保持你原样） ==========
is_webdriver = driver.execute_script("return navigator.webdriver")
print("navigator.webdriver:", is_webdriver)

langs = driver.execute_script("return navigator.languages")
print("navigator.languages:", langs)

vendor = driver.execute_script("return navigator.vendor")
platform = driver.execute_script("return navigator.platform")
print("navigator.vendor:", vendor)
print("navigator.platform:", platform)

webgl_info = driver.execute_script("""
   const canvas = document.createElement('canvas');
   const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
   const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
   return {
     vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
     renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
   };
""")

print("WebGL vendor:", webgl_info["vendor"])
print("WebGL renderer:", webgl_info["renderer"])

print("当前页面 title:", driver.title)

input("按回车退出浏览器...")
driver.quit()
