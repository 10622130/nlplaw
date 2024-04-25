import pandas as pd

# 讀取CSV文件
csv_file_path = 'csvconvert.py'
df = pd.read_csv(csv_file_path)

# 將DataFrame轉換為JSON格式
json_data = df.to_json(orient='records', lines=True)

# 寫入JSON文件
json_file_path = 'taichung.json'
with open(json_file_path, 'w') as json_file:
    json_file.write(json_data)
