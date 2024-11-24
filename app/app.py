from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agent import useragent_main, clear_provider_history, clear_user_history
from agent import provider_welcome, provide_agent_main
from db import user_get_reservation, user_get_review, put_review, delete_reservation, get_reviews, get_reservations
from db import provider_get_space, provider_update_space

load_dotenv()
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# Default ids
user_id = 0
provider_id = 0

# User side chat
@app.route('/userAgent', methods=['POST'])
def handle_user_agent():
    data = request.get_json()
    content = data.get("content")
    if content is None :
        return jsonify({"error":"'content' is null"}), 400
    print("POST receive: ", data)
    return jsonify(useragent_main(content=content, tries=0, user_id=user_id))

# Read reservation list
@app.route('/userReservation/<int:user_id>', methods=['GET'])
def handle_user_reservation(user_id):
    return jsonify(user_get_reservation(user_id=user_id))

# Delete reservation
@app.route('/reservation/<int:resv_id>', methods=['DELETE'])
def handle_reservation(resv_id):
    return jsonify(delete_reservation(resv_id=resv_id))

# List space review
@app.route('/spaceReview/<int:space_id>', methods=['GET'])
def handle_space_review(space_id):
    return jsonify(get_reviews(space_id=space_id))

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

# Welcome comment
@app.route('/providerWelcome', methods=['GET'])
def handle_provider_welcome():
    return jsonify(provider_welcome(provider_id=provider_id))

# Provider main agent
@app.route('/providerAgent', methods=['POST'])
def handle_provider_agent():
    data = request.get_json()
    content = data.get('content')
    return jsonify(provide_agent_main(content=content, provider_id=provider_id))

# Get & Update space
@app.route('/providerSpace', methods=['GET', 'PUT'])
def handle_provider_space():
    if request.method == 'GET':
        return jsonify({"space":provider_get_space(provider_id=provider_id)})
    elif request.method == 'PUT' :
        data = request.get_json()
        space = data.get('space')
        return jsonify(provider_update_space(space=space, provider_id=provider_id))
# Get reservations
@app.route('/providerReservations', methods=['GET'])
def handle_provider_reservations():
    return jsonify(get_reservations(provider_id=provider_id))
# Space reviews
@app.route('/providerReviews', methods=['GET'])
def handle_provider_reviews():
    return jsonify(get_reviews(provider_id=provider_id))

# Clear chat history
@app.route('/clsUser', methods=['GET'])
def handle_user_clear():
    clear_user_history()
    return jsonify({})
@app.route('/clsProvider', methods=['GET'])
def handle_provider_clear():
    clear_provider_history()
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
