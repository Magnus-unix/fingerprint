// extra.js
// 获取 cookie 字符串
export function getCookieFingerprint() {
    try {
        // 注意：document.cookie 只能获取非 HttpOnly 的 cookie
        return document.cookie || '';
    } catch (e) {
        console.error("获取 cookie 失败:", e);
        return '';
    }
}

// 获取公网 IP（这里用 ipify 免费 API）
export async function getIPFingerprint() {
    try {
        const res = await fetch('https://api.ipify.org?format=json');
        const data = await res.json();
        return data.ip || '';
    } catch (e) {
        console.error("获取 IP 失败:", e);
        return '';
    }
}
