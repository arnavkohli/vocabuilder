import os, pymongo, random
import smtplib
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from datetime import timedelta
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def test_and_time(func):
    def wrapper(*args, **kwargs):
        timeStart = datetime.now()
        result = func(*args, **kwargs)
        timeEnd = datetime.now()
        print (f"Runtime: {(timeEnd - timeStart).seconds / 60} minutes.")
        return result
    return wrapper

def read_template(filename):
    with open(os.path.join(os.getenv('STATIC_FOLDER'), filename), 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

message_template = read_template('email.html')

def send_email(word, emails):
	print (f"[VOCABUILDER] Preparing to send email..")
	# set up the SMTP server
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(os.getenv('SENDER_ADDR'), os.getenv('SENDER_PWD'))
	print (f"[VOCABUILDER] Logged in through {os.getenv('SENDER_ADDR')}!")
	
	for index, email in enumerate(emails):
	    msg = MIMEMultipart()       # create a message

	    # add in the actual person name to the message template
	    message = message_template.substitute(
	    		WORD=word.get('word'),
	    		TYPE=word.get('type'),
	    		MEANING=word.get('meanings'),
	    		EXAMPLE_1=word.get('examples')[0],
	    		EXAMPLE_2=word.get('examples')[1],
	    		EXAMPLE_3=word.get('examples')[2],
	    		SYNONYMS=', '.join(word.get('synonyms'))
	    	)

	    # setup the parameters of the message
	    msg['From'] = os.getenv('SENDER_ADDR')
	    msg['To'] = email
	    msg['Subject']="Vocabuilder: Word of the day is here!"

	    # add in the message body
	    msg.attach(MIMEText(message, 'html'))

	    # send the message via the server set up earlier.
	    s.send_message(msg)

	    print (f"[VOCABUILDER] Sent to {email}")


def get_random_word(collection, should_be_high_frequency=True):
	print (f"[VOCABUILDER] Getting random word...")
	count = collection.estimated_document_count()
	if should_be_high_frequency:
		words = [x for x in collection.find({"is_high_frequency_word" : True})]
	else:
		words = [x for x in collection.find()]
	randomIndex = random.randint(0, len(words))
	word = words[randomIndex]
	print (f"[VOCABUILDER] Found `{word.get("word")}`")
	return word

@test_and_time
def send_new_word_via_email():
	client = pymongo.MongoClient(os.getenv("MONGO_CONN"))

	db = client.vocabuilder
	new_words_table = db.new_magoosh_words
	old_words_table = db.old_magoosh_words
	
	random_word = get_random_word(new_words_table, should_be_high_frequency=True)
	
	new_words_table.remove(random_word)
	random_word['last_sent'] = datetime.now()
	old_words_table.insert(random_word)

	send_email(random_word, emails=eval(os.getenv("EMAILS")))
