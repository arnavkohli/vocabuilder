import os, random
import pymongo
import smtplib
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Word:
    def __init__(self, word: str, type : str, meaning: str, examples: list, is_high_frequency_word: bool, synonyms: list):
        self.word = word
        self.type = type
        self.meaning = meaning
        self.examples = examples
        self.is_high_frequency_word = is_high_frequency_word
        self.synonyms = synonyms

    def json(self) -> dict:
        return {
            "word" : self.word,
            "type" : self.type,
            "meanings" : self.meaning,
            "examples" : self.examples,
            "is_high_frequency_word": self.is_high_frequency_word,
            "synonyms" : self.synonyms
        }

def get_synonyms_and_examples_from_thesaurus(word: str) -> (list, list):
    url = f"https://www.thesaurus.com/browse/{word}"
    headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}

    request = requests.get(url, headers=headers)
    if request.status_code != 200:
        return [], []

    soup = bs(request.text, 'html.parser')

    div = soup.find("div", attrs = {"id" : "meanings"})
    
    try:
        synonyms = [i.text.strip() for i in div.find_all("li")[:5]]
    except:
        synonyms = []


    divs = soup.find_all("div", attrs = {"class" : "css-1m7xl5f e1wcrhwt0"})
    examples = []
    for index, div in enumerate(divs):
        if index == 4:
            break
        span = div.find("span")
        examples.append(span.text)

    return synonyms, examples

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

def _delete_key_from_dict(dict, key):
    if key not in dict:
        return dict
    del dict[key]
    return dict

def get_all_words(collection: pymongo.collection) -> list:
    '''
        Given the collection instance, 
        retrieve all words from it.
    '''
    return [_delete_key_from_dict(word, "_id") for word in collection.find()]

# ETL Workers
def _extract_example_from_meaning(meaning: str) -> (str, str):
    foundUpperAt = None

    for index, letter in enumerate(meaning):
        if index == 0 or letter in [" ", ".", ",", ";", ":"]:
            continue

        if letter == letter.upper():
            foundUpperAt = index
            break
    if foundUpperAt:
        return  meaning[:foundUpperAt - 1], meaning[foundUpperAt:]
    else:
        return meaning, ""

def _extract_word_data_from_line(line: str, line_no: int, lines: int, is_high_frequency_word: bool=False) -> Word:
    line_split = line.split("):")
    word, type = line_split[0].split(" ")
    # Clean the type ffs
    type = type[1:]

    synonyms, examples = get_synonyms_and_examples_from_thesaurus(word)

    meaning = line_split[1].strip()

    magoosh_example = lines[line_no + 2]

    if "):" in magoosh_example:
        meaning, magoosh_example = _extract_example_from_meaning(meaning)

    if magoosh_example:
        examples = [magoosh_example] + examples

    return Word(
                    word=word,
                    type=type,
                    meaning=meaning,
                    examples=examples,
                    is_high_frequency_word=is_high_frequency_word,
                    synonyms=synonyms
                )

def _extract_word_name_from_line(line: str) -> str:
    line_split = line.split("):")
    word, type = line_split[0].split(" ")
    return word

def extract_to_dict(fp: str, existing_word_names: str, hfw_only=True) -> list:
    '''
        Extract words into a dict.
    '''
    raw_data = open(fp, "r").read()
    lines = raw_data.split("\n")

    all_words = []
    total_lines = len(lines)

    skip = -1
    highFreqWord = True
    
    for line_no, line in enumerate(lines):
        if line_no == skip:
            continue
        if 'Basic Words' == line.strip():
            highFreqWord = False
            # Early stoppage for HFWs
            if hfw_only:
                break
        elif '):' in line:
            word = _extract_word_name_from_line(line)
            if word in existing_word_names:
                skip = line_no + 2
                continue
            word = _extract_word_data_from_line(line, line_no, lines, is_high_frequency_word=highFreqWord)

            try:
                all_words.append(word.json())

                skip = line_no + 2

                print (f"[{line_no + 1} / {total_lines}] {word.word}")
            except Exception as err:
                print (err)
                print (f"skipping {word}")
    return all_words
