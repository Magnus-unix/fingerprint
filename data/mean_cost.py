import json
import os, sys
os.chdir(sys.path[0])

def analyze_signal_size_kb(json_file, start_id=666, end_id=785):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    selected = [item for item in data if start_id <= item.get("id", 0) <= end_id]

    if not selected:
        print(f"❌ 没有找到 id 在 {start_id}~{end_id} 的数据")
        return

    fields = ["level1Signals", "level2Signals", "level3Signals"]
    sizes = {f: [] for f in fields}

    for record in selected:
        for field in fields:
            val = record.get(field)
            if val is not None:
                try:
                    size_kb = len(json.dumps(val, ensure_ascii=False).encode("utf-8")) /1024
                    sizes[field].append(size_kb)
                except Exception:
                    continue

    print(f"✅ 信号字段体积统计 (id: {start_id} ~ {end_id})")
    for field, kb_list in sizes.items():
        if kb_list:
            n = len(kb_list)
            avg_kb = sum(kb_list) / n
            variance = sum((x - avg_kb) ** 2 for x in kb_list) / n
            std_dev = variance ** 0.5
            print(f"{field:15s} → 平均: {avg_kb:.3f} KB | 方差: {variance:.3f} | 标准差: {std_dev:.3f} (样本数: {n})")
        else:
            print(f"{field:15s} → 无数据")

    return sizes


if __name__ == "__main__":
    json_file = "parsed_records_flat.json"
    analyze_signal_size_kb(json_file)
