#處理資料夾內多個檔案
# 將txt轉為json為Question Answer 
# ETL
######################################
# 檔案1與檔案2及3有不同的正規表達式
## 超連結刪除
## 句子尾端 數字清除
## 如果有指定文字則整題不納入(請見、請參考、https、法律百科、本百科、參閱)
## 內含html格式 刪除
## 重複題目刪除

import os
import re
import json

# def main(folder_path,output_path):
def main(input_file,output_path):
    # 取得資料夾中的所有檔案名稱
    # txt_files = get_all_txt_files(folder_path)
    txt_file = input_file
    # print(txt_files)
    data=[]
    # for txt_file in txt_files:
    # print(txt_file)
    with open(txt_file, 'r', encoding='utf-8') as file:
        # 分別讀取每個txt檔 並處理超連結
        text = file.read()
        # print(text)
        txt = re.sub(r'\[.*?\]', '', text)
        pattern = re.compile(r'<a\s.*?href="(.*?)".*?>(.*?)<\/a>')
        txt = re.sub(pattern, '', txt)
        # print(text)
    # 將讀取出的txt檔 依正規表達式 拆分成兩段
    # 1
    # matches = re.findall(r'Crawling Page \d+ -\n([^A]*)\nAnswer:([^C]*)', txt, re.DOTALL)
    # 2、3
    pattern2 = re.compile(r'\nCrawling Page \d+ - (.+?)\nAnswer: (.+?)\n', re.DOTALL)
    matches = pattern2.findall(txt)

    # print(matches)

    # Initialize list to store question-answer pairs
    # qa_pairs type is list
    qa_pairs = []

    # Print the results
    for match in matches:
        question = match[0].strip()
        answer = match[1].strip() if len(match) > 1 else None
        # print("Question:", question)
        # print("Answer:", answer)
        # print("------")

        # Add question-answer pair to the list
        qa_pairs.append({"instruction": question, "input": "", "output": answer})
        # print(qa_pairs)

        # 處理換行符號
        for item in qa_pairs:
            # 對字典中的 instruction 和 output 鍵對應的值進行替換
            if "instruction" in item:
                item["instruction"] = item["instruction"].replace("\n", "").replace("Question: ", "").replace(" ","").replace("　　","")
                # item["instruction"] = re.sub(r'[\（\(][^）\)]*法律百科[^）\)]*[\）\)]', '', item["instruction"])
                
            if "output" in item:
                item["output"] = item["output"].replace("\n", "").replace("Question: ", "")
                # item["output"] = re.sub(r'[\（\(][^）\)]*法律百科[^）\)]*[\）\)]', '', item["output"])
        
    filtered_data = []

    for item in qa_pairs:
        if isinstance(item, dict):
            # 如果有指定文字則整題不納入(請見、請參考、https、法律百科、本百科、參閱)
            if "請見" not in item["instruction"] and "請參考" not in item["instruction"] and "https" not in item["instruction"]\
                    and "法律百科" not in item["instruction"]and "本百科" not in item["instruction"]and "參閱" not in item["instruction"]\
                    and "請見" not in item["output"] and "請參考" not in item["output"] \
                    and "https" not in item["output"]and "法律百科" not in item["output"]\
                    and "本百科" not in item["output"]and "參閱" not in item["output"]:
                filtered_data.append(item)
        else:
            print(f"Skipping invalid item: {item}")
    # print(filtered_data)
            
    # 刪除字串尾的數字
    for item in filtered_data:
        # print(item)
        item["instruction"] = remove_trailing_numbers(item["instruction"])
        item["output"] = remove_trailing_numbers(item["output"])

    # 要都非空值
    filtered_data = [item for item in filtered_data if item["instruction"] and item["output"]]
    
    with open("test.json", 'w', encoding='utf-8') as json_file:
        json.dump(filtered_data, json_file, ensure_ascii=False, indent=2)

    unique_qa_pairs = []
    seen_instructions = set()

    for item in filtered_data:
        instruction = item["instruction"]
        if instruction not in seen_instructions:
            seen_instructions.add(instruction)
            unique_qa_pairs.append(item)  
    # print(unique_qa_pairs) 

    data.extend(unique_qa_pairs)

        # Print the resulting JSON
        # print(filtered_data)
    # 寫入 JSON 檔案
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        # json_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)

# 刪除字串尾的是數字
def remove_trailing_numbers(text):
    return re.sub(r'\d+$', '', text)        

# 從資料夾取得每個.txt結尾的檔案路徑
def get_all_txt_files(folder_path):
    txt_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files

# 資料夾路徑
# folder_path = r"C:\Users\T14 Gen 3\Desktop\Project\Data\lawabc\txt"
input_file=r"C:\Users\T14 Gen 3\Desktop\Project\Data\lawabc\txt\legis_3.txt"
output_path = r"C:\Users\T14 Gen 3\Desktop\Project\Data\lawabc\txt2\output_3.json"

#處理資料夾 
# if __name__ == "__main__":
#     main(folder_path,output_path)

# 處理一個檔案
if __name__ == "__main__":
    main(input_file,output_path)
