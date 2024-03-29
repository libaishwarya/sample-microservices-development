from functools import wraps
import json
from flask import Flask, jsonify, request
import uuid
import hashlib
from store import user as userstore
import datetime
import jwt
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(id, is_admin = False):
    payload = {
        'user_id' : id,
        'is_admin' : is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1) 
    }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY', 'my_name'), algorithm='HS256')
    
    return token

def register_user(name, email, password, is_admin = False):
        hashed_password = hash_password(password)
        user_id = str(uuid.uuid4())
        
        err = userstore.insert_user(user_id, name, email, hashed_password, is_admin)
        if err != None:
            return 500

        return jsonify({"id": user_id}), 201

def login_user(email, password):
    try:
        user = userstore.get_user(email, hash_password(password))
        
        if user is None:
            return jsonify({'message': 'Invalid credentials'}), 401
        
        user_id = user[0]
        is_admin = user[4]
        token = generate_token(user_id,is_admin)
        
        return jsonify({'token': token, 'id': user_id}), 200
            
    except Exception as e:
        return jsonify({'message': 'An error occurred'}), 500

        
def view_user(ids):
    try:
        user = userstore.read_user(ids)
        return jsonify(user), 200
    except:
        return jsonify({'message': 'An error occurred'}), 500
    
def update_user(ids,name,email):
    try:
        err = userstore.user_update(ids,name,email)
        if err is not None:
            return jsonify(err), 500
        
        return "",204
    except:
        return jsonify({'message': 'An error occurred'}), 500

def delete_user(ids):
    try:
        user = userstore.user_delete(ids)
        return jsonify({"message": "User deleted successfully"}), 200
        
    except:
        return jsonify({'message': 'An error occurred'}), 500
    
    
