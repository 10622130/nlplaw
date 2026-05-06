import pinecone      

# 可以藉由以下程式碼建立
def create_index(index_name):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            index_name,
            dimension=1536,
            metric='cosine'
        )
        # 等待 index 建立完成
        while not pinecone.describe_index(index_name).status['ready']:
            time.sleep(1)