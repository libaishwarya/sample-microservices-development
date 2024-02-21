from flask import Flask, jsonify, request
import os
import mysql.connector
import bcrypt
import uuid
import datetime
import jwt
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my_name')

def generate_token(id):
    payload = {
        'user_id' : id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expiration time
    }
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')
    return token


app.secret_key = os.environ.get('SECRET_KEY')

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
    try:
        hashed_password = hash_password(password)
        user_id = str(uuid.uuid4())
        
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction()
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
            conn.start_transaction()
            cursor.execute('SELECT * FROM user_management WHERE email = %s AND password = %s', (email, hash_password(password)))
            user = cursor.fetchone()
            conn.commit()
            conn.close()
            if  user is None:
                return "",401
            token = generate_token(user[0])
            return jsonify({'token': token, 'id': user[0]}), 200
    return 500

@app.route("/users", methods=['GET'])
def user_view():
    if request.method == 'GET':
        
        if 'Authorization' not in request.headers:
            return "", 401
            
        token_parts = request.headers['Authorization'].split()
        if len(token_parts) == 2:
            token_type, token = token_parts
        if not token:
            return jsonify({'message': 'Token is missing'}), 401        
        try: 
            decoded_token = jwt.decode(token, app.secret_key, algorithms=['HS256'])   
            user_id = decoded_token['user_id']

            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute('SELECT * FROM user_management WHERE id = %s ', (user_id,))
            user = cursor.fetchone()
            conn.close()
            if user:
                    user_dict = {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                    }
                    return jsonify(user_dict), 200
            else:
                    return jsonify({"error": "User not found"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
    return jsonify({'message': 'Internal Server Error'}), 500


@app.route("/users", methods=['PUT'])
def user_update():
    if request.method == 'PUT':
        
        if 'Authorization' not in request.headers:
            return "",401
        
        token_parts = request.headers['Authorization'].split()
        if len(token_parts) == 2:
            token_type, token = token_parts
        else:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            decoded_token = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            
            data = request.json
            name = data.get('name')
            email = data.get('email')
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute('UPDATE user_management SET name = %s, email = %s WHERE id = %s', (name, email, user_id))
            conn.commit()
            conn.close()
            return jsonify({"message": "User updated successfully"}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
    
    return "", 500
    
@app.route("/users", methods=['DELETE'])
def user_delete():
    if request.method == 'DELETE':
        if 'Authorization' not in request.headers():
            return "", 401
        
        token_parts = request.headers['Authorization'].split()
        if len(token_parts) == 2:
            token_type, token = token_parts
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            decoded_token = jwt.decode(token, app.secret_key, algorithms=['HS256'])   
            user_id = decoded_token['user_id']
            
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute('DELETE FROM user_management WHERE id = %s', (user_id,))
            conn.commit()
            conn.close()
            return jsonify({"message": "User deleted successfully"}), 200
        except Exception :
            conn.rollback()
            return 500

if __name__ == '__main__':
    app.run(debug=True)