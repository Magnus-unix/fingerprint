"""
OpenClaw vs 其他 POC 对标分析脚本

读取各个 POC 输出目录中的 JSON 报告，
进行对比分析，生成对标报告。
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


RESULTS_DIRS = {
    "openclaw": Path(__file__).parent / "outputs",
    "nodriver": Path(__file__).parent.parent / "nodriver_poc" / "outputs",
    "patchright": Path(__file__).parent.parent / "patchright_poc" / "outputs",
    "seleniumbase": Path(__file__).parent.parent / "seleniumbase_poc" / "outputs",
}


def load_latest_report(poc_name: str, results_dir: Path) -> Dict[str, Any]:
    """加载最新的 JSON 报告"""
    if not results_dir.exists():
        return {"error": f"目录不存在: {results_dir}"}

    # 找最新的报告文件
    json_files = sorted(results_dir.glob("*_*.json"), reverse=True)
    if not json_files:
        return {"error": f"未找到 JSON 报告: {results_dir}"}

    latest_file = json_files[0]
    try:
        with open(latest_file) as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"读取失败: {e}"}


def analyze_fingerprint(fingerprint: Dict[str, Any]) -> Dict[str, Any]:
    """分析指纹数据"""
    if not fingerprint:
        return {}

    return {
        "webdriver_detected": fingerprint.get("webdriver", False),
        "ua": fingerprint.get("userAgent", "")[:50],
        "lang": fingerprint.get("language", ""),
        "platform": fingerprint.get("platform", ""),
        "hw_concurrency": fingerprint.get("hardwareConcurrency"),
        "chrome_runtime_detected": fingerprint.get("hasChromeRuntime", False),
    }


def compare_pocs() -> None:
    """
    对标分析所有 POC
    """
    print(f"\n{'='*80}")
    print("OpenClaw vs 其他 POC 对标分析")
    print(f"{'='*80}\n")

    results_summary = {}

    for poc_name, results_dir in RESULTS_DIRS.items():
        print(f"\n【{poc_name.upper()}】")
        print("-" * 40)

        report = load_latest_report(poc_name, results_dir)

        if "error" in report:
            print(f"❌ {report['error']}")
            continue

        # 处理单次运行和多次迭代的情况
        if "results" in report:  # 多次迭代（汇总报告）
            print(f"🔄 多次迭代: {report.get('iterations', 'N/A')}")
            print(f"✓ 成功率: {report.get('success_rate', 'N/A')}")
            print(f"🪤 Honeypot 触发率: {report.get('honeypot_trigger_rate', 'N/A')}")

            # 分析第一次运行的指纹
            if report["results"]:
                first_result = report["results"][0]
                fingerprint = analyze_fingerprint(first_result.get("fingerprint"))
                for key, val in fingerprint.items():
                    print(f"   {key}: {val}")

                honeypot = first_result.get("honeypot", {})
                print(f"   honeypot_triggered: {honeypot.get('triggered', False)}")

        else:  # 单次运行
            print(f"✓ 登录成功: {report.get('success', False)}")

            fingerprint = analyze_fingerprint(report.get("fingerprint"))
            for key, val in fingerprint.items():
                print(f"   {key}: {val}")

            honeypot = report.get("honeypot", {})
            if honeypot:
                print(f"   honeypot_triggered: {honeypot.get('triggered', False)}")

        results_summary[poc_name] = report

    # 生成对标总结
    print(f"\n{'='*80}")
    print("📊 对标总结")
    print(f"{'='*80}\n")

    # 统计检测结果
    detection_comparison = {}
    for poc_name, report in results_summary.items():
        if "error" in report:
            continue

        if "results" in report:
            # 多次迭代：取成功率和触发率
            success_rate = report.get("success_rate", "0%")
            trigger_rate = report.get("honeypot_trigger_rate", "0%")
            print(f"{poc_name:15} | 成功率: {success_rate:>6} | Honeypot: {trigger_rate:>6}")
        else:
            # 单次运行
            success = report.get("success", False)
            honeypot = report.get("honeypot", {})
            if honeypot:
                triggered = honeypot.get("triggered", False)
            else:
                triggered = False
            success_str = "✓" if success else "✗"
            trigger_str = "✓ 触发" if triggered else "✗ 未触发"
            print(f"{poc_name:15} | 登录: {success_str} | Honeypot: {trigger_str}")

    print(f"\n{'='*80}")
    print("💡 分析建议")
    print(f"{'='*80}\n")

    # 性能建议
    webdriver_detections = []
    for poc_name, report in results_summary.items():
        if "error" in report:
            continue

        if "results" in report and report["results"]:
            fp = report["results"][0].get("fingerprint", {})
        else:
            fp = report.get("fingerprint", {})

        if fp and fp.get("webdriver"):
            webdriver_detections.append(poc_name)

    if webdriver_detections:
        print(f"⚠️  以下框架被检测到 navigator.webdriver: {', '.join(webdriver_detections)}")
    else:
        print(f"✓ 所有框架均通过 navigator.webdriver 检测")

    print(f"\n📝 建议:")
    print(f"   1. OpenClaw 作为新框架，可参考 patchright/seleniumbase 的反检测配置")
    print(f"   2. 重点关注 Honeypot 陷阱触发率，应尽量避免")
    print(f"   3. 持续监控指纹一致性评分，特别是音频和 Canvas 指纹")

    # 保存对标报告
    output_path = RESULTS_DIRS["openclaw"] / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "results_summary": results_summary,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n✓ 对标报告已保存: {output_path}")


if __name__ == "__main__":
    compare_pocs()
