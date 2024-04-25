import json
from sklearn.model_selection import train_test_split

# 讀取原始資料
with open('law_data.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 將資料分割成訓練集和測試集
train_lines, test_lines = train_test_split(lines, test_size=0.3, random_state=42)

# 寫入 train-api.jsonl
with open('train_lawdata.jsonl', 'w', encoding='utf-8') as f_train:
    f_train.writelines(train_lines)

# 寫入 test-api.jsonl
with open('remain_lawdata.jsonl', 'w', encoding='utf-8') as f_test:
    f_test.writelines(test_lines)
