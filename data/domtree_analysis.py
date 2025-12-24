import json
import os

def load_dom_data_from_file(file_path, target_id):
    """
    从本地 JSON 文件中加载指定 ID 的数据块
    """
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data_list = json.load(f)
            
            # 查找 id 为 target_id 的数据块
            # 这里使用了生成器表达式，找到第一个匹配项即停止，效率更高
            target_block = next((item for item in data_list if item.get('id') == target_id), None)
            
            if target_block:
                return target_block.get('domData')
            else:
                print(f"未在文件中找到 id 为 {target_id} 的数据块")
                return None
                
        except json.JSONDecodeError:
            print("错误：JSON 文件格式不正确")
            return None

def analyze_dom(dom):
    stats = {
        "total_nodes": 0,
        "visible_nodes": 0,
        "interactive_nodes": 0,
        "visible_interactive": 0,
        "script_text_nodes": 0
    }

    def walk(node):
        stats["total_nodes"] += 1
        if node.get("visible"):
            stats["visible_nodes"] += 1
        if node.get("interactive"):
            stats["interactive_nodes"] += 1
            if node.get("visible"):
                stats["visible_interactive"] += 1
        if node.get("tag") == "script" and node.get("text"):
            stats["script_text_nodes"] += 1

        for c in node.get("children", []):
            walk(c)

    walk(dom["domTree"])
    return stats


# --- 主程序执行 ---

# 1. 指定文件名（请确保该文件在当前目录下）
FILE_NAME = 'parsed_records_flat.json'  # 换成你真实的文件名
TARGET_ID = 866

# 2. 获取数据
dom_data = load_dom_data_from_file(FILE_NAME, TARGET_ID)

if dom_data:
    # 3. 执行分析
    print(analyze_dom(dom_data)) 