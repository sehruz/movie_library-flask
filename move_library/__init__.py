import secrets
from flask import Flask
from move_library.routes import pages
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def create_app():
    app=Flask(__name__)
    app.config['MONGODB_URI']=os.environ.get('MONGODB_URI')
    app.config['SECRET_KEY']=os.environ.get(
        "SECRET_KEY", 'ABAYgc59HbrAHswmTXRoUJH_X28jjCIzcWYu-gihfqE'
    )

    app.db=MongoClient(app.config['MONGODB_URI']).microblog
    app.register_blueprint(pages)
    return app

