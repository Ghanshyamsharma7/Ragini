import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["ragini_db"]

chunks_collection = db["chunks"]
ingested_files_collection = db["ingested_files"]  # tracks processed PDFs