import json

# 讀取原始資料
with open('all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 寫入新的資料到 JSON Lines 檔案
with open('prompt-jsonl.jsonl', 'w', encoding='utf-8') as f:
    for item in data:
        json_line = json.dumps({"prompt": item["instruction"], "completion": item["output"]}, ensure_ascii=False)
        f.write(json_line + '\n')
