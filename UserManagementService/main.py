from flask import Flask, jsonify, request
import os
import mysql.connector
import bcrypt
import uuid

app = Flask(__name__)

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
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@app.route("/users", methods=['POST'])
def create_users():
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

@app.route("/users/<string:id>", methods=['GET'])
def user_view(id):
    if request.method == 'GET':
        try:
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute('SELECT * from user_management where id = %s', (id,))
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
        except Exception :
            conn.rollback()
            return 500

@app.route("/users/<string:id>", methods=['PUT'])
def user_update(id):
    if request.method == 'PUT':
        try:
            data = request.json
            name = data.get('name')
            email = data.get('email')
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute('UPDATE user_management SET name = %s, email = %s WHERE id = %s', (name, email, id))
            conn.commit()
            conn.close()
            return jsonify({"message": "User updated successfully"}), 200
        except Exception :
            conn.rollback()
            return 500
    
@app.route("/users/<string:id>", methods=['DELETE'])
def user_delete(id):
    if request.method == 'DELETE':
        try:
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute('DELETE FROM user_management WHERE id = %s', (id,))
            conn.commit()
            conn.close()
            return jsonify({"message": "User deleted successfully"}), 200
        except Exception :
            conn.rollback()
            return 500

if __name__ == '__main__':
    app.run(debug=True)