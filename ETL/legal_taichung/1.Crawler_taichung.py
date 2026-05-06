# 資料來源:台中市政府法制局 https://www.legal.taichung.gov.tw/30340/23515?Page=1&PageSize=30&type=

from bs4 import BeautifulSoup
import requests
import pandas as pd

all_data = pd.DataFrame(columns=['question', 'answer'])

for pages in range (1,5) :
    # 替換 url 中的 {pages} 部分
    url = f"https://www.legal.taichung.gov.tw/30340/23515?Page={pages}&PageSize=30&type="
        # 使用requests獲取網頁內容
        # print(f"url:{url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有 li 標籤下的 a 標籤
    all_links = soup.select('section.list li a')
    
    # 提取 href 屬性的值
    href_values = [f"https://www.legal.taichung.gov.tw{link['href']}" for link in all_links]
    for href_value in href_values:
        # number = soup.find(class_='numb')
        url=href_value
        # print(number)
        # print(url)
        if url.endswith("/post"):

            # print(url)
            response = requests.get(url)
            response.raise_for_status()  # 檢查是否有錯誤的 HTTP 狀態碼
            # 在這裡處理正常情況下的 response
            soup = BeautifulSoup(response.text, 'html.parser')
            # soup.find(class_="cpArticle")
            article_text=soup.find('article').text.strip()
            separator = None
            if "回答：" in article_text:
                question,answer=article_text.split("回答：",1)
            elif "A：" in article_text:
                question,answer=article_text.split("A：",1)
            else:
                center_div = soup.find('div', class_='center')
                if center_div:
                    header = center_div.find('header')
                    if header:
                        h2_tag = header.find('h2')
                        if h2_tag:
                            question = h2_tag.text.strip()
                            print(question)
                        else:
                            print("未找到 h2 標記")
                    else:
                        print("未找到 header 標記")
                else:
                    print("未找到 center div 標記")
                    # question = header.find('h2').strip()
                            # question=soup.find('header').text.strip()
                answer=soup.find('article').text.strip()
                
            # print(question,answer)
            # print(article_text)
            # question = soup.find('article', text='問題：').find_next('p').text.strip()
            # answer = soup.find('p', text='回答：').find_next('p').text.strip()

            temp_data = pd.DataFrame(columns=['question', 'answer'])
            temp_data = pd.concat([temp_data, pd.DataFrame({'question': [question], 'answer': [answer]})],
                                        ignore_index=True)
            # print(temp_data)
        all_data = pd.concat([all_data, temp_data], ignore_index=True)
# #最後匯出成excel 
# print(all_data)
all_data.to_excel(r"C:\Users\T14 Gen 3\Desktop\Project\Data\legal_taichung\all_data.xlsx", index=False)

    


