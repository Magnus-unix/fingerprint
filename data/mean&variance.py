import json
import math
import os, sys
os.chdir(sys.path[0])

def analyze_duration(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    durations = []
    for record in data:
        # 有可能 duration 在最外层或 fingerprint 内部
        dur = None
        if "duration" in record:
            dur = record["duration"]
        elif isinstance(record.get("fingerprint"), dict):
            dur = record["fingerprint"].get("duration")

        if isinstance(dur, (int, float)):
            durations.append(dur)

    if not durations:
        print("没有找到任何有效的 duration 数据。")
        return

    n = len(durations)
    mean = sum(durations) / n
    variance = sum((x - mean) ** 2 for x in durations) / n
    stddev = math.sqrt(variance)
    sorted_desc = sorted(durations, reverse=True)
    
    # 打印最大值和最小值
    print(f"最大值 (max): {sorted_desc[0]:.2f} ms")
    print(f"最小值 (min): {sorted_desc[-1]:.2f} ms")

    # 确定要打印的数量，最多5个
    count_to_print = min(n, 5) 
    print(f"\n最大的 {count_to_print} 个 duration 值:")
    for i in range(count_to_print):
        print(f"  {i+1}. {sorted_desc[i]:.2f} ms")
    print(f"\n最小的 {count_to_print} 个 duration 值:") 
    for i in range(1,count_to_print):
        print(f"  {i}. {sorted_desc[-i]:.2f} ms")
    print(f"共有 {n} 条有效数据")
    print(f"平均值 (mean): {mean:.4f} ms")
    print(f"方差 (variance): {variance:.4f}")
    print(f"标准差 (stddev): {stddev:.4f}")

    return mean, variance, stddev

if __name__ == "__main__":
    analyze_duration("parsed_records_flat.json")
