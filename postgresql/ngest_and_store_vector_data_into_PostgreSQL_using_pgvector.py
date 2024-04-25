import openai
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector

# 遠端連接
connection_string = "dbname=postgres user=postgres password=520330 host=localhost port=5432"

# 连接到本地 PostgreSQL 数据库
conn = psycopg2.connect(connection_string)
cur = conn.cursor()

# Register pgvector extension
register_vector(conn)

# Helper function: Get top 1 most similar documents from the database
def get_top1_similar_docs_with_distance(query_embedding, conn):
    embedding_array = np.array(query_embedding)
    cur = conn.cursor()
    # Get the top 1 most similar documents using the KNN <=> operator
    cur.execute("SELECT mix, embedding <-> %s AS distance FROM embeddings ORDER BY distance LIMIT 1", (embedding_array,))
    top1_docs_and_distance = cur.fetchall()
    return top1_docs_and_distance

# Helper function: get text completion from OpenAI API
# Note we're using the latest gpt-3.5-turbo-0613 model
def get_completion_from_messages(messages, model="gpt-3.5-turbo-16k-0613", temperature=0.4, max_tokens=700):
    openai.api_key = ''
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]


# Helper function: get embeddings for a text
def get_embeddings(text):
    openai.api_key = ''
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input = text.replace("\n"," ")
    )
    embedding = response['data'][0]['embedding']
    return embedding

# Function to process input with retrieval of most similar documents from the database
def process_input_with_retrieval(user_id, user_input, conn):
    delimiter = "```"

    # Step 1: Retrieve the last 3 conversation pairs (questions and answers) for the user
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM conversation WHERE user_id = %s ORDER BY timestamp DESC LIMIT 2", (user_id,))
    conversation_pairs = cur.fetchall()
    cur.close()  # Close the cursor after use

    # Step 2: Get documents related to the user input from the database
    related_docs_and_distance = get_top1_similar_docs_with_distance(get_embeddings(user_input), conn)

    # 如果距离超过阈值，则不提供回答
    distance_threshold = 0.6  # 根据需要调整阈值
    if related_docs_and_distance[0][1] > distance_threshold:
        return "很抱歉，我無法找到足夠相關的資訊來回答您的問題。"

    system_message = f"""
    您好，我是法律小幫手。
    在回答您的問題之前，我會先評估提出的情況是否有可能違反法律。
    - 如果有法律問題，我將具體指出可能違反的法律條文，並提供相關的法律建議。
    - 如果判斷提出的問題不涉及法律領域，我可能無法提供答案。
    請注意，我的回答是基於一般性的法律知識，具體案件請諮詢專業律師。
    """

    # system_message = f"""
    # 您好，我是法律小幫手。
    # 在回答您的問題之前，我會先評估提出的情況是否有可能違反法律。
    # - 如果有法律問題，我將具體指出可能違反的法律條文，並提供相關的法律建議。
    # - 如果判斷提出的問題不涉及法律領域，我可能無法提供答案。
    # 請注意，我提供的回答將基於一般性法律知識，並不針對任何具體的法律條文或個案進行解釋，具體案件請諮詢專業律師。
    # """
    # Step 3: Prepare messages to pass to the model, including the recent conversation history
    messages = [{"role": "system", "content": system_message}]

    # 强调当前正在处理的问题
    messages.append({"role": "system", "content": "現在，讓我們來回答您的最新問題："})

    # Add current user input
    messages.append({"role": "user", "content": f"{delimiter}{user_input}{delimiter}"})


    # Add recent conversation pairs with appropriate roles
    for i, (question, answer) in enumerate(reversed(conversation_pairs), start=1):
        messages.append({"role": "user", "content": f"歷史問題 {i}: {question}"})
        if answer:  # Only add non-empty answers
            messages.append({"role": "assistant", "content": f"歷史回答 {i}: {answer}"})

    # Add related documents as part of the assistant's response
    if related_docs_and_distance and related_docs_and_distance[0][1] <= distance_threshold:
        messages.append({"role": "assistant", "content": f"根據您的問題，我找到了以下相關資料來幫助您理解可能的解決方案:\n{related_docs_and_distance[0][0]}"})
    else:
        messages.append({"role": "assistant", "content": "我在目前的資料庫中沒有找到與您的問題直接相關的資料。"})

    # Step 4: Get the completion from the OpenAI API using the prepared messages
    final_response = get_completion_from_messages(messages)

    return final_response



