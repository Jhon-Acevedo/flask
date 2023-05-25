from bson import json_util
# from flask_pymongo import MongoClient
import certifi
from pymongo import MongoClient

ca = certifi.where()


def db_connection(mongo_uri, db_name):
    try:
        client_mongo = MongoClient(mongo_uri)
        db = client_mongo[str(db_name)]
    except Exception as e:
        raise Exception(e)
    return db
