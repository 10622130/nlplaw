# 將問題及答案的json依條件合在一起

import json
import csv
def combine_json(json_file1, json_file2):
    with open(json_file1, 'r', encoding='utf-8') as file:
        data1 = json.load(file)

    with open(json_file2, 'r', encoding='utf-8') as file:
        data2 = json.load(file)

    combined_data = []

    for item1 in data1:
        for item2 in data2:
            if item1['Year'] == item2['Year'] and item1['Subject'] == item2['Subject'] and item1['Num'] == item2['Num']:
                if len(item2['Answer']) == 1:
                    combined_item = {
                        "Year": item1['Year'],
                        "Subject": item1['Subject'],
                        "Num": item1['Num'],
                        "Qus": item1['Qus'],
                        "Answer": item2['Answer']
                    }
                    combined_data.append(combined_item)

    return combined_data

json_file2 = r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\answer_json.json"
json_file1 = r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\question_json_103_112.json"

combined_data = combine_json(json_file1, json_file2)

with open(r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\combined_Q&A_2.json", 'w', encoding='utf-8') as file:
    json.dump(combined_data, file, ensure_ascii=False, indent=4)

# 保存成 CSV 檔案
csv_file_path = r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\combined_Q&A_2.csv"
with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Year", "Subject", "Num", "Qus", "Answer"])
    writer.writeheader()
    for item in combined_data:
        writer.writerow(item)

print("Successfully combined and saved to 'combined.json'!")
