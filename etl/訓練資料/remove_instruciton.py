import json

# 讀取原始 JSON 檔案，使用 UTF-8 編碼
with open('llama2_tw_law.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 創建新的資料格式
new_data = []
for item in data:
    new_item = {
        "input": item["instruction"],
        "output": item["output"]
    }
    new_data.append(new_item)

# 寫入新的 JSON 檔案
with open('llama2_tw_law1.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)
