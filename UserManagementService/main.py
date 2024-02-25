from functools import wraps
from flask import Flask, jsonify, request
import os
import mysql.connector
import bcrypt
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my_name')

db_config = {
    'host': os.environ.get('DATABASE_HOST', 'localhost'),
    'user': os.environ.get('DATABASE_USER', 'root'),
    'password': os.environ.get('DATABASE_PASSWORD', 'PASSWORD'),
    'database': os.environ.get('DATABASE_NAME', 'user_management')
}

def get_connection():
    return mysql.connector.connect(**db_config)

if __name__ == '__main__':
    app.run(debug=True)