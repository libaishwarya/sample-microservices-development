from functools import wraps
from flask import Flask
from routes import user

app = Flask(__name__)

app.register_blueprint(user.app, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)