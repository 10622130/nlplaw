from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# 假设您已经设置了数据库连接字符串
DATABASE_URL = "dbname=postgres user=postgres password=520330 host=localhost port=5432"

# 连接数据库的函数
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/random-question', methods=['POST'])
def random_question():
    # 从POST请求的JSON体中获取数据
    data = request.json
    year_subject = data.get('year_subject')
    
    try:
        year, subject = year_subject.split(' ')
    except ValueError:
        return jsonify({'error': 'Invalid input format. Please use "year subject" format.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
    SELECT year, subject, question, answer FROM exam_questions
    WHERE year = %s AND subject = %s
    ORDER BY RANDOM()
    LIMIT 1
    """
    
    cur.execute(query, (year, subject))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return jsonify({
            'year': result[0],
            'subject': result[1],
            'question': result[2],
            'answer': result[3]
        })
    else:
        return jsonify({'error': 'No records found matching the criteria'})

if __name__ == '__main__':
    app.run(debug=True)