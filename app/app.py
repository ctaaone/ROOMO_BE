from flask import Flask, request, jsonify
from flask_cors import CORS
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
