import json

# 讀取原始 JSON 檔案，使用 UTF-8 編碼
with open('llama2_tw_law1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍歷資料，計算每筆資料中 "input" 和 "output" 標籤內中文字數的總和
new_data = []
for item in data:
    input_text = item["input"]
    output_text = item["output"]
    total_length = len(input_text) + len(output_text)
    # 檢查是否超過1000個中文字
    if total_length <= 1000:
        new_data.append(item)

# 寫入新的 JSON 檔案
with open('llama2_tw_law2.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)
