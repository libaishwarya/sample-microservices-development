from functools import wraps
from flask import Flask, jsonify, request
import uuid
import hashlib
from store import user

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
        hashed_password = hash_password(password)
        user_id = str(uuid.uuid4())
        
        err = user.insert_user(user_id, name, email, hashed_password)
        if err != None:
            return 500

        return jsonify({"id": user_id}), 201