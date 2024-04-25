import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# 定义 PostgreSQL 连接信息
DATABASE_URI = ""
# 定义 CSV 文件路径
CSV_FILE_PATH = r''
# 读取 CSV 文件到 Pandas DataFrame
df = pd.read_csv(CSV_FILE_PATH)
# 创建 PostgreSQL 数据库引擎
engine = create_engine(DATABASE_URI)
# 将 DataFrame 写入 PostgreSQL 数据库
df.to_sql('QA', engine, if_exists='replace', index=False)

print("CSV 文件成功导入 PostgreSQL 数据库。")