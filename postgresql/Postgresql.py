import psycopg2
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
import os
from ngest_and_store_vector_data_into_PostgreSQL_using_pgvector import *

connection_string = "dbname=postgres user=postgres password=520330 host=localhost port=5432"


def insert_user(user_id, user_name):
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, user_name) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
                (user_id, user_name))
    conn.commit()
    conn.close()

def insert_conversation(user_id, question, answer):
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute("INSERT INTO Conversation (user_id, question, answer) VALUES (%s, %s, %s)",
                (user_id, question, answer))
    conn.commit()
    conn.close()

