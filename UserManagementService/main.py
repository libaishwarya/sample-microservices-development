from functools import wraps
from flask import Flask, jsonify, request
import os
from routes import user

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my_name')


app.register_blueprint(user.app, url_prefix='/')




if __name__ == '__main__':
    app.run(debug=True)