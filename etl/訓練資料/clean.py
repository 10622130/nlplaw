import json

# 讀取JSON文件
json_file_path = 'taichung.json'
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# 將 Python 對象轉換為 JSON 字符串
json_string = json.dumps(json_data, ensure_ascii=False, indent=2)

# 使用相同的 json.loads 再次轉換為 Python 對象
json_data_again = json.loads(json_string)

# 將所有的 "question" 換成 "instruction"，"answer" 換成 "output"
def replace_keys(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            new_key = key.replace("question", "instruction").replace("answer", "output")
            new_obj[new_key] = replace_keys(value)
        return new_obj
    elif isinstance(obj, list):
        return [replace_keys(item) for item in obj]
    else:
        return obj

json_data_transformed = replace_keys(json_data_again)


def remove_newlines(obj):
    if isinstance(obj, str):
        return obj.replace("\n", "")
    elif isinstance(obj, list):
        return [remove_newlines(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: remove_newlines(value) for key, value in obj.items()}
    else:
        return obj

json_data_without_newlines = remove_newlines(json_data_transformed)


def add_input_tag(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if key == "instruction":
                new_obj["instruction"] = value
                new_obj["input"] = ""  # 在這裡加入input標籤
            elif key == "output":
                new_obj["output"] = value
            else:
                new_obj[key] = add_input_tag(value)
        return new_obj
    elif isinstance(obj, list):
        return [add_input_tag(item) for item in obj]
    else:
        return obj

json_data_with_input = add_input_tag(json_data_without_newlines)

# print(json_data_transformed)

# 將 Python 對象轉換為 JSON 字符串
json_string_transformed = json.dumps(json_data_with_input, ensure_ascii=False, indent=2)

# 寫入轉換後的JSON文件
output_json_file_path = 'taichung-clean.json'
with open(output_json_file_path, 'w', encoding='utf-8') as output_json_file:
    output_json_file.write(json_string_transformed)
