import pymongo
from .workers import get_random_word, send_email

def send_random_word_via_email(mongo_conn_url: str, database: str, \
		new_words_collection_name: str, old_words_collection_name: str, \
			sender_addr: str, sender_pwd: str, emails: list, template_path: str, should_be_high_frequency: bool = True):
	'''
		Retrieves a random word from the new words
		collection, sends an email to the emails provided
		and moves the record into the old words coolection.
	'''
	client = pymongo.MongoClient(mongo_conn_url)

	db = client[database]
	new_words_table = db[new_words_collection_name]
	old_words_table = db[old_words_collection_name]
	
	random_word = get_random_word(new_words_table, should_be_high_frequency=should_be_high_frequency)
	
	#new_words_table.remove(random_word)
	#random_word['last_sent'] = datetime.now()
	#old_words_table.insert(random_word)

	send_email(
		word_data=random_word, 
		sender_addr=sender_addr,
		sender_pwd=sender_pwd,
		emails=emails,
		template_path=template_path
	)