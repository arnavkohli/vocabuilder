import os, random
import pymongo
import smtplib
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Lambda Daily Run Workers

def read_template(template_path: str) -> Template:
    '''
        Given the file name, looks for the HTML template
        with the specified file name in the folder with path 
        STATIC_FOLDER of the lambda function.
    '''
    with open(template_path, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def send_email(word_data: dict, sender_addr: str, sender_pwd: str, emails: list, template_path: str) -> bool:
    '''
        Send emails containing word details to given list of addresses.
    '''
    print (f"[VOCABUILDER] Preparing to send email(s)..")
    # set up the SMTP server
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender_addr, sender_pwd)
    print (f"[VOCABUILDER] Logged in through {sender_addr}!")

    # read template
    message_template = read_template(template_path)
    
    all_sent = True
    for index, email in enumerate(emails):
        try:
            msg = MIMEMultipart()       # create a message

            # add in the actual person name to the message template
            message = message_template.substitute(
                    WORD=word_data.get('word'),
                    TYPE=word_data.get('type'),
                    MEANING=word_data.get('meanings'),
                    EXAMPLE_1=word_data.get('examples')[0],
                    EXAMPLE_2=word_data.get('examples')[1],
                    EXAMPLE_3=word_data.get('examples')[2],
                    SYNONYMS=', '.join(word_data.get('synonyms'))
                )

            # setup the parameters of the message
            msg['From'] = sender_addr
            msg['To'] = email
            msg['Subject']="Vocabuilder: Word of the day is here!"

            # add in the message body
            msg.attach(MIMEText(message, 'html'))

            # send the message via the server set up earlier.
            s.send_message(msg)

            print (f"[VOCABUILDER] Sent to {email}")
        except Exception as err:
            print (f"[VOCABUILDER] There was an error in sending an email to: {email}; Error: {err}")
            all_sent = False

    return all_sent

# MongoDB workers
def get_random_word(collection: pymongo.collection, should_be_high_frequency=False) -> dict:
    '''
        Given the collection instance, retrieve details
        for a random word.
    '''
    print (f"[VOCABUILDER] Getting random word...")
    count = collection.estimated_document_count()
    if should_be_high_frequency:
        words = [x for x in collection.find({"is_high_frequency_word" : should_be_high_frequency})]
    else:
        words = [x for x in collection.find()]
    randomIndex = random.randint(0, len(words))
    word_data = words[randomIndex]
    print (f"[VOCABUILDER] Found `{word_data.get('word')}`")
    return word_data
