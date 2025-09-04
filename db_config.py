from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb://localhost:27017/")  # Change if remote
    db = client["whatsapp_clone_new"]
    return db
