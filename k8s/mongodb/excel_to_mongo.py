import os
import sys
import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

if not all([MONGO_URI, MONGO_DB, MONGO_COLLECTION]):
    raise SystemExit("MongoDB secrets are missing")

if len(sys.argv) != 2:
    raise SystemExit("Usage: python excel_to_mongo.py <excel_file.xlsx>")

excel_file = sys.argv[1]

df = pd.read_excel(excel_file)
df = df.where(pd.notnull(df), None)

records = df.to_dict("records")

client = MongoClient(MONGO_URI)
collection = client[MONGO_DB][MONGO_COLLECTION]

result = collection.insert_many(records)
print(f"Inserted {len(result.inserted_ids)} documents")
