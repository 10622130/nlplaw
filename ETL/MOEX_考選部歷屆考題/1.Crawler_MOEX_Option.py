# 爬蟲考選部選擇題
# https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx
# 下載成PDF
# 年度103~112年
# check html 年度 標籤尾數

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import re


# 創建一個 WebDriver
driver = webdriver.Chrome()
url=r"https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx"

# 打開網頁
driver.get(url)

# ###step 0###
# 獲取完整的 HTML 結構
page_source = driver.page_source

soup = BeautifulSoup(page_source, 'html.parser')

# ###step1 輸入年份###
# 使用 WebDriverWait 等待下拉式選單出現
start_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//select[@title="考試年度(起)"]')))

#選擇開始年份 (2014/103)
start_dropdown = Select(start_dropdown)
start_dropdown.select_by_value('2014') 
time.sleep(2)

# 使用 WebDriverWait 等待下拉式選單出現
end_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//select[@title="考試年度(迄)"]')))

# 選擇結束年份
end_dropdown = Select(end_dropdown)
end_dropdown.select_by_value('2016')  

time.sleep(2)

quiz_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//select[@name="ctl00$holderContent$ddlExamCode"]')))
quiz_select = Select(quiz_dropdown)

# 獲取所有選項的值
all_options_values = [option.get_attribute("value") for option in quiz_select.options]

# 選擇尾數為 ___ 的選項
# selected_options_values = []
for option_value in all_options_values:
    if option_value.endswith("110"):
        quiz_select.select_by_value(option_value)

        # 使用 WebDriverWait 等待按鈕出現
        search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="ctl00_holderContent_divSearchSimple"]/input[@name="ctl00$holderContent$btnSearch"]')))

        # 點擊查詢按鈕
        search_button.click()

        # 假設已經有 soup 對象
        download_links = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//a[@class="exam-question-ans"]'))
)

        # 遍歷每個連結，執行下載操作
        for download_link in download_links:
            # 獲取下載連結的 href 屬性
            pdf_link = f"{download_link.get_attribute('href')}"
            # print(f"link={pdf_link}")
            year = pdf_link.split("code=")[1][:3]

            # 創建存檔資料夾
            folder_name = f"C:/Users/T14 Gen 3/Desktop/Project/Data/MOEX/{year}"
            print(f"folder_name:{folder_name}")

            file_name=f"{download_link.get_attribute('title')}"
            file_name=file_name.strip().replace("另開視窗，開啓","").replace("(Pdf檔)","")
            file_name = re.sub(r'[\\/:"*?<>|]', '', file_name)

            os.makedirs(folder_name, exist_ok=True)
            response = requests.get(pdf_link,timeout=5,verify=False)
            file_path = os.path.join(folder_name, file_name + ".pdf")
            # 檢查網頁回應
            if response.status_code == 200:
                with open(f"{file_path}", 'wb') as pdf_file:
                    pdf_file.write(response.content)
            else:
                print(f"Failed to download PDF. Status code: {response.status_code}")
            time.sleep(5)
                
            # 將 PDF 下載到本地文件
            # with open('downloaded_file.pdf', 'wb') as pdf_file:
            #     pdf_file.write(response.read())
        quiz_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//select[@name="ctl00$holderContent$ddlExamCode"]')))
        )

# 關閉瀏覽器
driver.quit()