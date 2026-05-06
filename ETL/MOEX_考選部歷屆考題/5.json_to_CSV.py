import json
import csv

# 讀取JSON數據

with open(r"C:\Users\T14 Gen 3\Desktop\Project\Data\combine_json\all_result.json", 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# 開啟CSV檔案並寫入數據
csv_file_path = r"C:\Users\T14 Gen 3\Desktop\Project\Data\combine_json\all_result.csv"

with open(csv_file_path, 'w', newline='',encoding="utf-8") as csv_file:
    # 創建CSV寫入器
    csv_writer = csv.writer(csv_file)

    # 寫入 CSV 標題
    header = json_data[0].keys()
    csv_writer.writerow(header)

    # 寫入數據行
    for entry in json_data:
        csv_writer.writerow(entry.values())

print(f'成功將JSON轉換為CSV，輸出文件位於：{csv_file_path}')
