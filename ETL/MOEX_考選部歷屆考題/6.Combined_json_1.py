# 合併Q&A from txt*3

import json
import glob


# 合併 json檔
# 指定檔案路徑的 pattern
file_pattern = r'C:\Users\T14 Gen 3\Desktop\Project\Data\lawabc\txt2\*.json'

# 讀取所有符合 pattern 的檔案
file_list = glob.glob(file_pattern)

# 儲存所有 JSON 對象的列表
all_data = []

# 逐一讀取檔案並合併到 all_data
for file_path in file_list:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        all_data.extend(data)

# 合併後的結果存放在 all_data 中
print(type(all_data))

# 將合併後的結果寫入一個新的檔案
output_file = r"C:\Users\T14 Gen 3\Desktop\Project\Data\lawabc\txt2\result.json"
with open(output_file, 'w', encoding='utf-8') as output:
    json.dump(all_data, output, ensure_ascii=False, indent=2)
