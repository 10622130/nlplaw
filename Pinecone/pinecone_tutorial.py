import pinecone
import openai
import configparser
from db import db

# Setup
config = configparser.ConfigParser()
config.read('config.ini')

# 調用embedding的OpenAPI
def get_embedding(question):
    openai.api_key = config.get("OpenAI", "api_key")
    response = openai.Embedding.create(
    model="text-embedding-ada-002",
    input = question
    )
    # 提取生成文本中的嵌入向量
    embedding = response['data'][0]['embedding']
    
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
    to_be_upsert = []

    for every in db:
        temp = {}
        temp['id'] = every['id']
        temp['values'] = get_embedding(every['question'])
        temp['metadata'] = {'question': every['question'],'answer': every['answer']}

        to_be_upsert.append(temp)

    return to_be_upsert

# 使用 Pinecone 索引進行向量檢索
def search_from_pinecone(index, query_embedding, k=1):
    results = index.query(vector=query_embedding,
                          top_k=k, include_metadata=True, namespace='first_try')
    return results

#################### Main function ####################
index = init_pinecone('test01') 
index.upsert(
    vectors=make_dataset(),
    namespace='first_try'
)


# 進行相似性搜索
try:
    index = init_pinecone("test01")
    question = "發生車禍怎麼辦？"
    query_embedding = get_embedding(question)
    qa_results = search_from_pinecone(index, query_embedding, k=1)   # k為尋找相似性最高
    print(qa_results["matches"][0]["metadata"]["answer"])

except Exception as e:
    print(f"An error occurred: {e}")