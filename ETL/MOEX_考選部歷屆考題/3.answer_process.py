# 處理答案卷成json

import pdfplumber as pr
import re
import os
import json

def extract_year__subject_from_path(file_path):
    # 從檔案路徑中提取年度信息
    # 假設路徑格式是 "C:\...\112\..."，你可以根據實際情況進行修改
    parts = file_path.split(os.path.sep)
    match = re.search(r'\([一二\d]+\)\((.*?)\)', file_path)
    # print(match)
    for part in parts:
        if part.isdigit():
            year=int(part)
    if match:
        subject = match.group(1)
    return year,subject

def read_all_pdfs(folder_path):
    pdf_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith("答案.pdf"):
                pdf_files.append(os.path.join(root, file))
    
    return pdf_files

# 將 Python 字典轉換成 JSON 格式並寫入檔案
def save_json(json_file_path,data):
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main(folder_path,json_file_path):
    # 初始化結果列表
    result_list = []
    pdf_files=read_all_pdfs(folder_path)
    # print(pdf_files)
    # 迴圈處理資料夾內的檔案
    for pdf_file in pdf_files:
        year,subject=extract_year__subject_from_path(pdf_file)
        # print(year,subject)
        with pr.open(pdf_file) as pdf:
            # print(pdf)
            ps = pdf.pages
            # print(ps)
            pg = ps[0]
            # print(pg)
            tables = pg.extract_tables()
            # print(tables)
        # 對每個子列表進行處理
        for i in range (0,9):
        # 提取題號和答案
            for j in range (1,11):
                questions = tables[i][0][j]
                answers = tables[i][1][j]
                questions=questions.replace("第","").replace("題","")
                print(f"questions:{questions} ",end="")
                print(answers)
                print("-------------")
                if answers =="":
                    break
                else:
                    result_dict={"Year":year,"Subject":subject,"Num":questions,"Answer":answers}
                        
                    # 將字典添加到結果列表
                    result_list.append(result_dict)
        # print(result_list)
        save_json(json_file_path,result_list)

pdf_path=r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX"
json_file_path = r"C:\Users\T14 Gen 3\Desktop\Project\Data\MOEX\answer_json.json"

main(pdf_path,json_file_path)


