# 爬取全國法規資料庫 近六個月熱門法條
# https://law.moj.gov.tw/Hot/Hot.aspx

import requests
from bs4 import BeautifulSoup
import json

url = "https://law.moj.gov.tw/Hot/Hot.aspx"

law_list=[]

# 解析HTML内容
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 查找<tbody>标签
tbody = soup.find('tbody')

# 查找<tbody>標籤下所有的<a>標籤
links = tbody.find_all('a', href=True)

replaced_links = []

# 依序跑每個link
for link in links:
    href = link['href']
    # replace成網址
    replaced_href = href.replace('AddHotLaw.ashx?', 'https://law.moj.gov.tw/LawClass/LawAll.aspx?')
    # append to list
    replaced_links.append(replaced_href)
print(replaced_links)

for replaced_link in replaced_links:
    response = requests.get(replaced_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    #提取法律名稱
    law = soup.find("a", id="hlLawName").text.strip()

    #提取所有法條的名稱
    articles = soup.find_all("div", class_="row")
    for article in articles:
        num_elem = article.find("a")

        # 查找所有class为line-0000的元素
        content_elems = article.find_all("div", class_=["line-0000", "line-0000 show-number","line-0004"])
        
        content = ""
        
        # Loop每個line-0000，合併到content
        for content_elem in content_elems:
            content += content_elem.text.strip() + " "
        
        # 檢查是否成功找到了法條編號和內容的元素
        if num_elem and content:
            num = num_elem.text.strip()

            law_info = {
                "instruction": law+num+"?",
                "input": "",
                "output": content
            }
            law_list.append(law_info)


# 保存為JSON
with open("law_data.json", "w", encoding="utf-8") as f:
    json.dump(law_list, f, ensure_ascii=False, indent=4)

print("法律信息已保存为 law_data.json 文件")
            
