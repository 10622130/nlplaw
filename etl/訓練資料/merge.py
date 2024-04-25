import json

# 讀取第一個JSON文件
json_file_path1 = 'all.json'
with open(json_file_path1, 'r', encoding='utf-8') as file1:
    data1 = json.load(file1)

# 讀取第二個JSON文件
json_file_path2 = 'law_data.json'
with open(json_file_path2, 'r', encoding='utf-8') as file2:
    data2 = json.load(file2)

# 合併兩個JSON數據
merged_data = {"data1": data1, "data2": data2}

# 寫入合併後的JSON文件
merge_json_file_path = 'llama2_tw_law.json'
with open(merge_json_file_path, 'w', encoding='utf-8') as merge_json_file:
    json.dump(merged_data, merge_json_file, ensure_ascii=False, indent=2)
