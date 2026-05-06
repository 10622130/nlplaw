
import json

def merge_dicts_with_same_keys(list1, list2):
    # 确定两个列表中所有字典共同具有的键
    common_keys = set(list1[0].keys()).intersection(set(list2[0].keys()))
    
    merged_list = []
    for dict1 in list1:
        for dict2 in list2:
            if all(dict1[key] == dict2[key] for key in common_keys):
                merged_dict = {**dict1, **dict2}  # 合并字典
                merged_list.append(merged_dict)
    
    return merged_list

# 示例
with open(r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\question_json_test.json", 'r', encoding='utf-8') as json_file:
    list1 = json.load(json_file)

with open(r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\answer_json.json", 'r', encoding='utf-8') as json_file:
    list2 = json.load(json_file)

merged_list = merge_dicts_with_same_keys(list1, list2)

with open(r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\merged_list.json", 'w', encoding='utf-8') as json_file:
    json.dump(merged_list, json_file, ensure_ascii=False, indent=4)


