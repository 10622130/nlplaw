from sklearn.model_selection import train_test_split
import json

# 讀取原始資料集
with open('llama2_tw_law2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 將資料集分割為訓練集和測試集
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# 將訓練集保存為 train.json
with open('llama2_tw_law2_0.8.json', 'w', encoding='utf-8') as file:
    json.dump(train_data, file, ensure_ascii=False, indent=2)

# 將測試集保存為 test.json
with open('llama2_tw_law2_0.2.json', 'w', encoding='utf-8') as file:
    json.dump(test_data, file, ensure_ascii=False, indent=2)
