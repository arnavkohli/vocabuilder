from vocabuilder.emailer import send_random_word_via_email

if __name__ == '__main__':
	MONGO_CONN_URL = "" 							 # MongoDB Connection URL
	DATABASE = "vocabuilder"						 # Database name
	NEW_WORDS_COLLECTION = "magoosh_words" 			 # New words collection name
	OLD_WORDS_COLLECTION = "old_magoosh_words"		 # Old words collection name
	SENDER_ADDR = "example@gmail.com"				 # Email address of sender
	SENDER_PWD = "abcd1234"							 # Password of sender
	EMAILS = ["test@gmail.com"]						 # List of emails to send the word to
	FP_TO_EMAIL_TEMPLATE = "./static/email.html"     # Path to email template

	send_random_word_via_email(
		mongo_conn_url=MONGO_CONN_URL,
		database=DATABASE,
		new_words_collection_name=NEW_WORDS_COLLECTION,
		old_words_collection_name=OLD_WORDS_COLLECTION,
		sender_addr=SENDER_ADDR,
		sender_pwd=SENDER_PWD,
		emails=EMAILS,
		template_path=FP_TO_EMAIL_TEMPLATE,
		should_be_high_frequency=True
	)