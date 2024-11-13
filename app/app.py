from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agent import useragent_main
from db import user_reservation_list, get_user_review, write_user_review

load_dotenv()
app = Flask(__name__)
CORS(app)

# User side
user_id = 1

# User side chat
@app.route('/userAgent', methods=['POST'])
def handle_user_agent():
    data = request.get_json()
    content = data.get("content")
    return jsonify(useragent_main(content=content, tries=0, user_id=user_id))

# Read reservation list
@app.route('/reservation', method=['GET'])
def handle_user_reservation():
    return jsonify(user_reservation_list(user_id=user_id))
    
# Write or read reviews
@app.route('/review/<int:space_id>', method=['GET', 'POST'])
def handle_user_review(space_id):
    if request.method == 'GET':
        return jsonify(get_user_review(space_id=space_id, user_id=user_id))
    elif request.method == 'POST':
        data = request.get_json()
        content = data.get('content')
        return jsonify({"review_id":write_user_review(space_id=space_id, user_id=user_id, content=content)})

# Provider side
# TODO

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
