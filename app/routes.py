from flask import Blueprint, request, jsonify
from app.validators import validate_user_input
from werkzeug.security import generate_password_hash
from app.db import authenticate_user, add_user_db, get_wallet_balance, handle_transaction
from app.auth import generate_jwt
import jwt
import os


routes = Blueprint('routes', __name__)
INTERNAL_JWT_SECRET = os.getenv("INTERNAL_SECRET_PHRASE")
JWT_SECRET = os.getenv("SECRET_PHRASE")

@routes.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    required_fields = ["name", "email", "password", "pan_card", "dob"]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Missing fields: {', '.join(missing_fields)}"
        }), 400
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    pan_card = data.get('pan_card')
    dob = data.get('dob')

    validation_errors = validate_user_input(name, email, password, pan_card, dob)
    if validation_errors:
        return jsonify({"status": "error", "errors": validation_errors}), 400

    hashed_password = generate_password_hash(password)

    user_data = {
        "name": name,
        "email": email,
        "password": password,
        "pan_card": pan_card,
        "dob": dob,
    }
    db_response = add_user_db(name, email, hashed_password, pan_card, dob)
    if db_response["status"] == "error":
        return jsonify(db_response), 400

    return jsonify(db_response), 201

@routes.route('/users/login', methods=['POST'])
def login():

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    # Authenticate user
    auth_response = authenticate_user(email, password)
    if auth_response["status"] == "error":
        return jsonify(auth_response), 401

    # Generate JWT token
    user_id = auth_response["user_id"]
    token = generate_jwt(user_id)

    return jsonify({"status": "success", "token": token}), 200

@routes.route('/users/wallet', methods=['GET'])
def wallet_balance():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
    except jwt.ExpiredSignatureError:
        return jsonify({"status": "error","message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"status": "error", "message": "Invalid or missing token"}), 401

    # Fetch wallet balance
    response = get_wallet_balance(user_id)

    if response["status"] == "error":
        return jsonify(response), 404

    return jsonify(response), 200

@routes.route('/users/transaction', methods=['POST'])
def transaction():

    data = request.get_json()
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, INTERNAL_JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
    except jwt.ExpiredSignatureError:
        return jsonify({"status": "error","message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"status": "error", "message": "Invalid or missing token"}), 401

    required_fields = [ "transaction_type", "amount"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"status": "error", "message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    transaction_type = data['transaction_type']
    amount = data['amount']

    if transaction_type not in ["CREDIT", "DEBIT"]:
        return jsonify({"status": "error", "message": "Invalid transaction_type. Must be CREDIT or DEBIT"}), 400

    if not isinstance(amount, (int, float)) or amount < 0:
        return jsonify({"status": "error", "message": "Amount must be a positive integer or float value"}), 400

    response = handle_transaction(user_id, transaction_type, amount)
    status_code = 200 if response["status"] == "success" else 400
    return jsonify(response), status_code
