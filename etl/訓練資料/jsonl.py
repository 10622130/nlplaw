# import json

# # 讀取JSON文件中的數據
# with open('all.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# # 將instruction和output字段轉換為JSONL格式
# jsonl_data = {"messages": []}
# for item in data:
#     jsonl_data["messages"].append({"role": "system", "content": "You are a professional legal consultant that provides objective advice on every question."})
#     jsonl_data["messages"].append({"role": "user", "content": item["instruction"]})
#     jsonl_data["messages"].append({"role": "assistant", "content": item["output"]})

# # 將轉換後的數據寫入JSONL文件
# with open('all.jsonl', 'w', encoding='utf-8') as f:
#     json.dump(jsonl_data, f, ensure_ascii=False)

import json

# 讀取JSON文件中的數據
with open('law_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 將instruction和output字段轉換為JSONL格式
jsonl_data = []
for item in data:
    message = {
        "messages": [
            {"role": "system", "content": "法條索引"},
            {"role": "user", "content": item["instruction"]},
            {"role": "assistant", "content": item["output"]}
        ]
    }
    jsonl_data.append(message)

# 將轉換後的數據寫入JSONL文件
with open('law_data.jsonl', 'w', encoding='utf-8') as f:
    for message in jsonl_data:
        json.dump(message, f, ensure_ascii=False)
        f.write('\n')  # 換行

