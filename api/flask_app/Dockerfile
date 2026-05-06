# 使用 Python 3.10 的官方映像
FROM python:3.10

# 設置容器內工作目錄
WORKDIR /app

# 依賴套件不會頻繁變動 所以先複製 requirements.txt 進容器下載 讓docker build時可以利用cache
COPY requirements.txt /app

# 預防import error
ENV PYTHONPATH=/app

# 安裝必要的 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#  告訴開發者以外的人這個容器對接的port號，實際上這指令並沒有作用
EXPOSE 5002

# 使用 Gunicorn 啟動 Flask 應用程式
CMD ["gunicorn", "-b", "0.0.0.0:5002", "app:app"]
