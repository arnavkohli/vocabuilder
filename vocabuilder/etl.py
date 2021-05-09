import os
import pymongo
from workers import extract_to_dict, get_all_words

def run(mongo_conn_url: str, database: str, collection: str, fp: str):
	client = pymongo.MongoClient(mongo_conn_url)
	db = client[database]
	collection = db[collection]

	existing_words = get_all_words(collection)
	existing_word_names = [word.get("word") for word in existing_words]

	words_to_insert = extract_to_dict(fp, existing_word_names, hfw_only=True)
	if words_to_insert:
		collection.insert_many(words_to_insert)
	print (f"Words added: {len(words_to_insert)}")