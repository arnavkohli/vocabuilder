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
        print (f"Search Term: {kwargs.get('word', '').get('word')}")
        print (f"Sentences: {result}")
        return result
    return wrapper

@test_and_time
def get_example_sentences(*args, **kwargs):
	url = f"https://sentence.yourdictionary.com/{kwargs.get('word', '').get('word')}"
	headers = {
		"accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"accept-encoding" : "gzip, deflate, br",
		"accept-language" : "en-US,en;q=0.9",
		"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
	}
	request =  requests.get(url, headers=headers)
	
	if request.status_code != 200:
		return ['']

	soup = bs(request.text, 'html.parser')

	examples_div = soup.find_all('div', attrs = {'class' : 'sentence-item'})

	sentences = []
	for example_div in examples_div:
		sentences.append(example_div.text.strip())

	return sentences

def read_template(filename):
    with open(os.path.join(os.getenv('STATIC_FOLDER'), filename), 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

message_template = read_template('email.html')

def send_email(word, emails):
	# set up the SMTP server
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(os.getenv('SENDER_ADDR'), os.getenv('SENDER_PWD'))
	# For each contact, send the email:
	more_examples = get_example_sentences(word=word)
	
	for index, email in enumerate(emails):
	    msg = MIMEMultipart()       # create a message

	    # add in the actual person name to the message template
	    message = message_template.substitute(
	    		WORD=word.get('word'),
	    		TYPE=word.get('type'),
	    		MEANING=word.get('meaning'),
	    		EXAMPLE_1=word.get('example'),
	    		EXAMPLE_2=more_examples[0],
	    		EXAMPLE_3=more_examples[1]
	    	)

	    # setup the parameters of the message
	    msg['From'] = os.getenv('SENDER_ADDR')
	    msg['To'] = email
	    msg['Subject']="Vocabuilder: Word of the day is here!"

	    # add in the message body
	    msg.attach(MIMEText(message, 'html'))

	    # send the message via the server set up earlier.
	    s.send_message(msg)
	    
	    del msg
	    print (f"[DAG] Sent to {email}")


def get_random_word(collection, should_be_high_frequency=True):
	
	count = collection.estimated_document_count()
	print (count)
	if should_be_high_frequency:
		words = [x for x in collection.find({"is_high_frequency_word" : True})]
	else:
		words = [x for x in collection.find()]
	randomIndex = random.randint(0, len(words))
	
	return words[randomIndex]


def notify_via_email():
	client = pymongo.MongoClient(os.getenv("MONGO_CONN"))

	db = client.vocabuilder
	new_words_table = db.new_magoosh_words
	old_words_table = db.old_magoosh_words
	
	random_word = get_random_word(new_words_table, should_be_high_frequency=True)
	
	new_words_table.remove(random_word)
	random_word['last_sent'] = datetime.now()
	old_words_table.insert(random_word)

	send_email(random_word, emails=eval(os.getenv("EMAILS")))


if __name__ == '__main__':
	notify_via_email()