import os
from vocabuilder.etl import run

if __name__ == '__main__':
	MONGO_CONN_URL = "" 							 # MongoDB Connection URL
	DATABASE = "vocabuilder"						 # Database name
	COLLECTION = "magoosh_words"     				 # Collection name
	FP_TO_RAW_DATA = "./static/magoosh_raw_list.txt" # File path to raw list

	run(
		mongo_conn_url=MONGO_CONN_URL,
		database=DATABASE,
		collection=COLLECTION,
		fp=FP_TO_RAW_DATA
	)