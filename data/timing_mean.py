import json
import numpy as np
import os, sys
os.chdir(sys.path[0])

def analyze_timing(json_file, start_id=766, end_id=785):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 只保留 id 范围内的数据
    selected = [item for item in data if start_id <= item.get("id", 0) <= end_id]

    if not selected:
        print(f"❌ 没有找到 id 在 {start_id}~{end_id} 的数据")
        return

    # 统计字段
    fields = ["level1", "level2", "level3"]
    stats = {field: [] for field in fields}

    for record in selected:
        timing = record.get("timing", {})
        for field in fields:
            val = timing.get(field)
            if isinstance(val, (int, float)):
                stats[field].append(val)

    # 计算平均值
    result = {}
    for field, values in stats.items():
        if values:
            result[field] = {
                "count": len(values),
                "avg": np.mean(values),
                "std": np.std(values)
            }
        else:
            result[field] = {
                "count": 0,
                "avg": None,
                "std": None
            }

    print(f"✅ 统计结果 (id: {start_id} ~ {end_id})")
    for k, v in result.items():
        print(f"{k:8s} → 平均值: {v['avg']:.3f} | 方差: {v['std']:.3f} | 样本数: {v['count']}")

    return result


if __name__ == "__main__":
    json_file = "parsed_records_flat.json"   # 你的 JSON 文件名
    analyze_timing(json_file)
