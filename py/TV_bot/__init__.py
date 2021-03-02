#!/usr/bin/python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ngrok import run_with_ngrok

# web server config starts here #

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
run_with_ngrok(app)
db = SQLAlchemy(app)

# import comes here to avoid circular import error
from py.TV_bot import routes
