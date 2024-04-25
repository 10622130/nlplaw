import openai
import os
import pandas as pd
import numpy as np
import json
import tiktoken
import psycopg2
import ast
import pgvector
import math
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

#First, run export OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY...


# Get openAI api key by reading local .env file
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) 
openai.api_key  = os.environ['OPENAI_API_KEY'] 

# 讀取原始 CSV 檔案
input_csv_path = 'all_resultV1.csv'
df = pd.read_csv(input_csv_path)

# 合併問與答
df['mix'] = df['instruction'] + ' ' + df['output']

# 選擇需要的欄位，包括原本的問題、答案以及新合併的欄位
result_df = df[['instruction', 'output', 'mix']]

# 存成新的 CSV 檔案
output_csv_path = 'all_resultV2.csv'
result_df.to_csv(output_csv_path, index=False)

# print(f'Merged CSV saved to {output_csv_path}')

# Helper functions to help us create the embeddings

# Helper func: calculate number of tokens
def num_tokens_from_string(string: str, encoding_name = "cl100k_base") -> int:
    if not string:
        return 0
    # Returns the number of tokens in a text string
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Helper function: calculate length of essay
def get_essay_length(essay):
    word_list = essay.split()
    num_words = len(word_list)
    return num_words

# Helper function: calculate cost of embedding num_tokens
# Assumes we're using the text-embedding-ada-002 model
# See https://openai.com/pricing
def get_embedding_cost(num_tokens):
    return num_tokens/1000*0.0001

# Helper function: calculate total cost of embedding all content in the dataframe
def get_total_embeddings_cost():
    total_tokens = 0
    for i in range(len(df.index)):
        text = df['mix'][i]
        token_len = num_tokens_from_string(text)
        total_tokens = total_tokens + token_len
    total_cost = get_embedding_cost(total_tokens)
    return total_cost

# Create new list with small content chunks to not hit max token limits
# Note: the maximum number of tokens for a single request is 8191

# list for chunked content and embeddings
new_list = []
# Split up the text into token sizes of around 512 tokens
for i in range(len(df.index)):
    text = str(df['mix'][i])  # Ensure text is a string
    token_len = num_tokens_from_string(text)
    if token_len <= 512:
        new_list.append([df['instruction'][i], df['output'][i], df['mix'][i], token_len])
    else:
        # add content to the new list in chunks
        start = 0
        ideal_token_size = 512
        # 1 token ~ 3/4 of a word
        ideal_size = int(ideal_token_size // (4/3))
        end = ideal_size
        #split text by spaces into words
        words = text.split()

        #remove empty spaces
        words = [x for x in words if x != ' ']

        total_words = len(words)
        
        #calculate iterations
        chunks = total_words // ideal_size
        if total_words % ideal_size != 0:
            chunks += 1
        
        for j in range(chunks):
            if end > total_words:
                end = total_words
            new_content = words[start:end]
            new_content_string = ' '.join(new_content)
            new_content_token_len = num_tokens_from_string(new_content_string)
            if new_content_token_len > 0:
                new_list.append([df['instruction'][i], df['output'][i], df['mix'][i], token_len])
            start += ideal_size
            end += ideal_size


# Helper function: get embeddings for a text
def get_embeddings(text):
   response = openai.Embedding.create(
       model="text-embedding-ada-002",
       input = text.replace("\n"," ")
   )
   embedding = response['data'][0]['embedding']
   return embedding

# Create embeddings for each piece of content
for i in range(len(new_list)):
   text = new_list[i][1]
   embedding = get_embeddings(text)
   new_list[i].append(embedding)

# Create a new dataframe from the list
df_new = pd.DataFrame(new_list, columns=['題目', '答案', 'mix', 'tokens', 'embeddings'])
df_new.head()


# Save the dataframe with embeddings as a CSV file
df_new.to_csv('finished.csv', index=False)

# 本地连接
# connection_string = "dbname=demo02 user=postgres password=520330 host=localhost port=5432"

# 遠端連接
connection_string = "dbname=postgres user=postgres password=520330 host=localhost port=5432"

# 连接到本地 PostgreSQL 数据库
conn = psycopg2.connect(connection_string)
cur = conn.cursor()

#Batch insert embeddings and metadata from dataframe into PostgreSQL database
register_vector(conn)
cur = conn.cursor()
# Prepare the list of tuples to insert
data_list = [(row['題目'], row['答案'], row['mix'], (row['tokens']), np.array(row['embeddings'])) for index, row in df_new.iterrows()]
# Use execute_values to perform batch insertion
execute_values(cur, "INSERT INTO embeddings (題目, 答案, mix, tokens, embedding) VALUES %s", data_list)
# Commit after we insert all embeddings
conn.commit()