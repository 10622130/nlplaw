import json
import pandas as pd

# 讀取 Excel 文件
df = pd.read_excel(r"C:\Users\T14 Gen 3\Desktop\Project\Data\legal_taichung\result.xlsx")

# xlsx轉csv
df.to_csv(r"C:\Users\T14 Gen 3\Desktop\Project\Data\legal_taichung\result.csv", index=False)

# 將 DataFrame 轉換為 JSON 格式
json_data = []
for index, row in df.iterrows():
    question = row['question']
    answer = row['answer']
    
    # 創建 JSON 對象
    json_obj = {
        "instruction": question,
        "input": "",
        "output": answer
    }
    
    # 將 JSON 對象添加到列表中
    json_data.append(json_obj)

# 寫入 JSON 文件
with open(r"C:\Users\T14 Gen 3\Desktop\Project\Data\legal_taichung\result.json", 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
