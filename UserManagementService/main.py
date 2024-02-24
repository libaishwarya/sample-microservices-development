from functools import wraps
from flask import Flask, jsonify, request
import os
import mysql.connector
import bcrypt
import uuid
import datetime
import jwt
import hashlib
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my_name')

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    
    return False
    
def validate_password(password):
    if len(password) < 8 or len(password) > 20:
        return False
    
    return True
    
def generate_token(id):
    payload = {
        'user_id' : id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1) 
    }
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')
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
            decoded_token = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            
            if 'ids' in kwargs and kwargs['ids'] != decoded_token['user_id']:
                return jsonify({"message": "Mismatched user ID"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Expired token"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        return func(*args, **kwargs)
    return decorated_function

db_config = {
    'host': os.environ.get('DATABASE_HOST', 'localhost'),
    'user': os.environ.get('DATABASE_USER', 'root'),
    'password': os.environ.get('DATABASE_PASSWORD', 'PASSWORD'),
    'database': os.environ.get('DATABASE_NAME', 'user_management')
}

def get_connection():
    return mysql.connector.connect(**db_config)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

@app.route("/register", methods=['POST'])
def user_register(): 
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (validate_email(email) == True and validate_password(password)== True):
            return "",400
    else:
        try:
            hashed_password = hash_password(password)
            user_id = str(uuid.uuid4())
            
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction(readonly=False)
            cursor.execute('INSERT INTO user_management (id, name, email, password) VALUES (%s, %s, %s, %s)', (user_id, name, email, hashed_password))
            conn.commit()
            conn.close()
            return jsonify({"id": user_id}), 201
        except Exception :
            conn.rollback()
            return 500
    
@app.route("/login", methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid credentials'}), 401
    if data:
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction(readonly=True)
            cursor.execute('SELECT * FROM user_management WHERE email = %s AND password = %s', (email, hash_password(password)))
            user = cursor.fetchone()
            conn.commit()
            conn.close()
            if  user is None:
                return "",401
            token = generate_token(user[0])
            return jsonify({'token': token, 'id': user[0]}), 200
    return 500

@app.route("/users/<string:ids>", methods=['GET'])
@token_required
def user_view(ids):      
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction(readonly=True)
        cursor.execute('SELECT * FROM user_management WHERE id = %s ', (ids,))
        user = cursor.fetchone()
        conn.close()
        user_dict = {
                                "ids": user[0],
                                "name": user[1],
                                "email": user[2],
                                }
        return jsonify(user_dict), 200

@app.route("/users/<string:ids>", methods=['PUT'])
@token_required
def user_update(ids):         
            data = request.json
            name = data.get('name')
            email = data.get('email')
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction(readonly=False)
            cursor.execute('UPDATE user_management SET name = %s, email = %s WHERE id = %s', (name, email, ids))
            conn.commit()
            conn.close()
            return jsonify({"message": "User updated successfully"}), 200
    
@app.route("/users/<string:ids>", methods=['DELETE'])
@token_required
def user_delete(ids):
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction(readonly=False)
            cursor.execute('DELETE FROM user_management WHERE id = %s', (ids,))
            conn.commit()
            conn.close()
            return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)