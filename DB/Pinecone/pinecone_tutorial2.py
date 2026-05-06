import pinecone
from openai import OpenAI
import configparser
import pandas as pd

# Setup
config = configparser.ConfigParser()
config.read('config.ini')

client = OpenAI(api_key=config.get('OpenAI','api_key'))

# 調用embedding的OpenAPI
def get_embedding(question):
    response = client.embeddings.create(
    model="text-embedding-ada-002",
    input = question
    )
    # 提取生成文本中的嵌入向量
    embedding = response.data[0].embedding
    
    return embedding

# 設定 Pinecone 的初始化參數，創建一個索引對象
def init_pinecone(index_name):
    pinecone.init(
        api_key = config.get("pinecone", "api_key"),
        environment='gcp-starter'
    )
    index = pinecone.Index(index_name)
    return index

# 轉換資料結構
def make_dataset():
 
    df = pd.read_csv('高點法律題庫-5.xlsx - 訓練集.csv')
    df.to_dict()

    to_be_upsert = []

    for key, value in df.iterrows():
        temp = {}
        temp['id'] = value['題號']
        temp['values'] = get_embedding(value['題目'])
        temp['metadata'] = {'question': value['題目'],'answer': value['答案'], 'keyword': value['法律關鍵字']}

        to_be_upsert.append(temp)

    return to_be_upsert

# 使用 Pinecone 索引進行向量檢索
def search_from_pinecone(index, query_embedding, k=1):
    results = index.query(vector=query_embedding,
                          top_k=k, include_metadata=True, namespace='law_tb_01')
    return results

#################### Main function ####################
# index = init_pinecone('test01') 
# index.upsert(
#     vectors=make_dataset(),
#     namespace='law_tb_01'
# )


# 進行相似性搜索
try:
    index = init_pinecone("test01")
    question = "車禍"
    query_embedding = get_embedding(question)
    qa_results = search_from_pinecone(index, query_embedding, k=1)   # k為尋找相似性最高
    print(qa_results["matches"][0]["metadata"]["answer"])

except Exception as e:
    print(f"An error occurred: {e}")