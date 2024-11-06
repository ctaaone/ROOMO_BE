from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)


# User Side Chat
@app.route('/userAgent', methods=['POST'])
def handle_user_agent():
    data = request.get_json()
    content = data.get("content")

    # TODO : User Agent Process


    # TODO : Parsing Result


    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        query = "SELECT * FROM your_table WHERE your_column = %s"
        cursor.execute(query, (content,))
        result = cursor.fetchall()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
