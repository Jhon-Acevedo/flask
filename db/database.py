from pymongo import MongoClient
import certifi

ca = certifi.where()


def db_connection(mongo_uri, db_name):
    try:
        client = MongoClient(mongo_uri, tlsCAFile=ca)
        db = client[str(db_name)]
    except Exception as e:
        raise Exception(e)
    return db
