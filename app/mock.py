from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data = {
    "type" : "spaceList",
    "agentResponse":"에이전트의 응답입니다. \n 개행 문자 \n 다음은 공간 목록입니다.",
    "spaces": [
        {
            "id": 1,
            "name": "공간 A",
            "description": "공간 A에 대한 설명입니다.",
            "location": "서울",
            "reviews": ["리뷰 1", "리뷰 2", "리뷰 3"],
        },
        {
            "id": 2,
            "name": "공간 B",
            "description": "공간 B에 대한 설명입니다.",
            "location": "부산",
            "reviews": ["리뷰 3", "리뷰 4", "리뷰 1"],
        },
    ]
}

@app.route('/userAgent', methods=['POST'])
def user_agent_main():
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
