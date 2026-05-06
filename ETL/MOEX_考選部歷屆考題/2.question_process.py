# 處理試題卷成json

import pdfplumber as pr
import re
import os
import json
import fitz

def main(folder_path,json_file_path):
    pdf_files=read_all_pdfs(folder_path) #pdf_files格式為list
    questions_list = []
    # print(pdf_files)
    for pdf_file in pdf_files: #依序讀取每個pdf_file
        # print(pdf_file)
        ex_text=[]
        text=extract_text_from_pdf(pdf_file)
        # text=str(text)
        year,subject=extract_year__subject_from_path(pdf_file)
        # print(type(text))
        # print("---------------")
        # with open("text.txt","w",encoding="utf-8") as file:
        #     file.write(text)
        
        for key,value in text.items(): #讀取每個item中的value 即考試內容
            # print(key)
            # print(f"Before{value}")
            # pattern_to_remove = r"(\d+)年*公 務 人 員 特 種 考 試 司 法 官 考 試.*禁止使用電子計算器。"
            pattern_to_remove = r"(\d+)[年|\s]*(公[\s]*務[\s]*人[\s]*員[\s]*特[\s]*種[\s]*考[\s]*試[\s]*司[\s]*法[\s]*官[\s]*考[\s]*試).*禁止使用電子計算器。"
            pattern_to_remove_2 = r"代號.*頁次：(\d+)－(\d+)"
            pattern_to_remove_3=r"一、單一選擇題.*該題不予計分。"
            pattern_to_remove_4=r"二、複選題.*該題以零分計算。"
            value1 = re.sub(r'\n\s*\n', "\n", value, flags=re.MULTILINE)
            value2 = re.sub(pattern_to_remove, "", value1, flags=re.DOTALL) #去除特定字
            value3 = re.sub(pattern_to_remove_2, "", value2, flags=re.DOTALL)   
            value4 = re.sub(pattern_to_remove_3, "", value3, flags=re.DOTALL) #去除特定字
            value5 = re.sub(pattern_to_remove_4, "", value4, flags=re.DOTALL)   
            value6 = re.sub(r'\n\s*\n', '\n', value5, flags=re.MULTILINE | re.DOTALL)
            ex_text.append(value6)
        # print(type(ex_text))
        with open("value6.txt","w",encoding="utf-8") as file:
            for item in ex_text:
                file.write(item)
            # 读取文本文件内容
        with open("value6.txt", "r", encoding="utf-8") as file:
            text = file.readlines()
            # print(type(text))

        # 去除開頭的空白行
        while text and text[0].strip() == "" and text[1].strip() == "":
            text.pop(0)

        # 去除结尾的空白行
        while text and text[-1].strip() == "":
            text.pop()
        # print(type(text))
        # 將list轉成str
        text7 = ''.join(text)
        # print(text7)
            
        # 將題目編號和內容匹配出來
        matches = re.findall(r'(\d+)\s*\n(.+?)(?=\n\d+)', text7,re.MULTILINE | re.DOTALL)
        # print(matches)

        # # 打印出匹配結果
        for match in matches:
            Num= match[0]
            Qus=replace_options(match[1])
            # print(f"Num{Num}")
            # print(f"Qus{Qus}")
            # print("--------------------")
            questions_list.append({
                "Year": year,
                "Subject": subject,
                "Num": Num,
                "Qus": Qus
            })
            # print(questions_list)
    save_json(json_file_path,questions_list)

# 讀取pdf path to list
def read_all_pdfs(folder_path):
    pdf_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith("試題.pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

#讀取pdf檔案 to text 格式為dict  
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_dict = {}

    for page_number in range(doc.page_count):
        page = doc[page_number]
        text = page.get_text("text")
        text_dict[f"Page_{page_number + 1}"] = text.strip()

    doc.close()
    return text_dict    

# 處理英文標籤亂碼
def replace_options(text):
    # options = ['(A)', '(B)', '(C)', '(D)']
    replacements = {
        '': '(A)',
        '': '(B)',
        '': '(C)',
        '': '(D)'
    }
    replaced_text = text
    for code, replacement in replacements.items():
        replaced_text = re.sub(re.escape(code), replacement, replaced_text)
    return replaced_text

# 從檔案路徑中提取年度信息及科目
def extract_year__subject_from_path(file_path):
    # 假設路徑格式是 "C:\...\112\..."，可以根據實際情況進行修改
    parts = file_path.split(os.path.sep)
    # print(parts)
    match = re.search(r'\([一二\d]+\)\((.*?)\)', file_path)
    # print(match)
    for part in parts:
        if part.isdigit():
            year=int(part)
    if match:
        subject = match.group(1)
    return year,subject

# 將 Python 字典轉換成 JSON 格式並寫入檔案
def save_json(json_file_path,questions_list):
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(questions_list, json_file, ensure_ascii=False, indent=4)
    print("成功儲存json檔!")


folder_path=r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX"
json_file_path=r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\question_json_103_112.json"

main(folder_path,json_file_path)