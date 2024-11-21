from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agent import useragent_main
from db import user_get_reservation, user_get_review, put_review, delete_reservation

load_dotenv()
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# User side
user_id = 0

# User side chat
@app.route('/userAgent', methods=['POST'])
def handle_user_agent():
    data = request.get_json()
    content = data.get("content")
    return jsonify(useragent_main(content=content, tries=0, user_id=user_id))

# Read reservation list
@app.route('/userReservation/<int:user_id>', methods=['GET'])
def handle_user_reservation(user_id):
    return jsonify(user_get_reservation(user_id=user_id))

# Delete reservation
@app.route('/reservation/<int:resv_id>', methods=['DELETE'])
def handle_reservation(resv_id):
    return jsonify(delete_reservation(resv_id=resv_id))

# Write or read reviews
@app.route('/review/<int:space_id>', methods=['GET', 'POST'])
def handle_user_review(space_id):
    if request.method == 'GET':
        return jsonify(user_get_review(space_id=space_id, user_id=user_id))
    elif request.method == 'POST':
        data = request.get_json()
        content = data.get('content')
        return jsonify({"review_id":put_review(space_id=space_id, user_id=user_id, content=content)})

# Provider side
# TODO

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
