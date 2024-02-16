from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
import uuid

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'PASSWORD',  
    'database': 'user_management'
}

app.secret_key = "myname"

@app.route("/")
def main():
    return "Welcome to Home page"

@app.route("/add_users", methods=['POST'])
def create_users():
    if request.method == 'POST':
        try:
            data = request.json
            name = data.get('name')
            email = data.get('email')
            passwords = data.get('passwords')  
            hashed = bcrypt.hashpw(passwords.encode('utf-8') , bcrypt.gensalt()) #hashing password using salt hasing
            conn = mysql.connector.connect(**db_config)  
            cur = conn.cursor()
            id = str(uuid.uuid4())  #UUID generator
            print(id)
            cur.execute('INSERT INTO user_management (id, name, email, passwords) VALUES (%s, %s, %s, %s)', (id, name, email, hashed))
            conn.commit()
            conn.close()
            return jsonify(data), 201
        except Exception as e:
            return jsonify(error=str(e)), 400

    return jsonify({"error": "Method Not Allowed"}), 405

@app.route("/view_user/<string:id>", methods = ['GET'])
def view_users(id):
        try:
            conn = mysql.connector.connect(**db_config)  
            cur = conn.cursor()
            cur.execute('SELECT * from user_management where id = %s', (id,))
            user = cur.fetchone()
            conn.commit()
            conn.close()
            if user:
                user_dic = {
                    "id" : user[0],
                    "name" : user[1],
                    "email" : user[2],
                    # "password" : user[3] 
                }
                return jsonify(user_dic), 200
            else:
                return 404
        except Exception as e:
            return jsonify(error=str(e)), 500
        
@app.route("/update_user/<string:id>", methods=['PUT'])
def update_user(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute('SELECT * FROM user_management WHERE id = %s', (id,))
        user = cur.fetchone()
        conn.close()
        if user:
            data = request.json
            name = data.get('name')
            email = data.get('email')
            conn = mysql.connector.connect(**db_config)
            cur = conn.cursor()
            query = "UPDATE user_management SET name = %s, email = %s WHERE id = %s"
            dataa = (name, email, id) 
            cur.execute(query, dataa)
            conn.commit()
            conn.close()
            return jsonify({"message": "User updated successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify(error=str(e)), 500   
    
@app.route("/delete_user/<string:id>", methods = ['DELETE'])
def delete_user(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute('DELETE FROM user_management WHERE id = %s', (id,))
        conn.close()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify(error=str(e)), 500   
    
if __name__ == '__main__':
    app.run(debug=True)
