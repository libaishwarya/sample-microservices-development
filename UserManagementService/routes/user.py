from functools import wraps
from flask import Flask, jsonify, request
import bcrypt
import datetime
import jwt
import re
from manager import user
from flask import Blueprint
import os

from store.utils import get_connection

app = Blueprint('users_app', __name__)

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    
    return False
    
def validate_password(password):
    if len(password) < 8 or len(password) > 20:
        return False
    
    return True
    
def generate_token(ids):
    payload = {
        'user_id' : ids,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1) 
    }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY', 'my_name'), algorithm='HS256')
    
    return token

def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return jsonify({"message": "Missing token"}), 401
        token_parts = request.headers['Authorization'].split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return jsonify({"message": "Invalid token format"}), 401
        token = token_parts[1]
        try:
            decoded_token = jwt.decode(token, os.environ.get('SECRET_KEY', 'my_name'), algorithms=['HS256'])
            
            if 'ids' in kwargs and kwargs['ids'] != decoded_token['user_id']:
                return jsonify({"message": "Mismatched user ID"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Expired token"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        return func(*args, **kwargs)
    
    return decorated_function

@app.route("/register", methods=['POST'])
def user_register(): 
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (validate_email(email) == True and validate_password(password)== True):
            return "",400

    return user.register_user(name, email, password)
    
@app.route("/login", methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid credentials'}), 401

    return user.login_user(email, password)

@app.route("/users/<string:ids>", methods=['GET'])
@token_required
def user_view(ids):     
    return user.view_user(ids)

@app.route("/users/<string:ids>", methods=['PUT'])
@token_required
def user_update(ids):         
    data = request.json
    name = data.get('name')
    email = data.get('email')
    return user.update_user(name, email, ids)
    
    
@app.route("/users/<string:ids>", methods=['DELETE'])
@token_required
def user_delete(ids):
    return user.delete_user(ids)