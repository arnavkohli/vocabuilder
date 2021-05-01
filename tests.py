import os
import pytest
import pymongo
from workers import send_email, get_random_word

@pytest.fixture
def dummy_word_data():
	return {
		"word": "aberration",
		"type": "noun",
		"meanings": "a deviation from what is normal or expected",
		"examples": ["Aberrations in climate have become the norm: rarely a week goes by without some meteorological phenomenon making headlines.", "They were also an aberration from conventional music industry logic.", "January 6th was a culmination of the president’s actions, not an aberration from them.", "We will also be investigating any aberrations and issues in the mail-in voting process as we find them, and telling the stories of the people and communities impacted most.", "Our current era of seesawing power is the historical aberration, and as political scientist Frances Lee argues in her book Insecure Majorities, it has reshaped Congress and made bipartisan compromise nearly impossible."],
		"is_high_frequency_word": True,
		"synonyms": ["oddity", "peculiarity", "quirk", "delusion", "eccentricity"]
	}

@pytest.fixture
def tester_email():
	return os.getenv("TESTER_EMAIL")

@pytest.fixture
def new_words_collection():
	client = pymongo.MongoClient(os.getenv("MONGO_CONN"))
	db = client.vocabuilder
	new_words_collection = db.new_magoosh_words
	return new_words_collection

def test_send_email(dummy_word_data, tester_email):
	email_sent = send_email(
		word_data=dummy_word_data, 
		sender_addr=os.getenv("SENDER_ADDR"), 
		sender_pwd=os.getenv("SENDER_PWD"), 
		emails=[tester_email], 
		template_path=os.path.join(os.getcwd(), "static/email.html")
	)
	assert email_sent == True

def test_get_random_word(new_words_collection):
	random_word_data = get_random_word(collection=new_words_collection)
	assert random_word_data != {}

def test_get_random_hf_word(new_words_collection):
	random_word_data = get_random_word(collection=new_words_collection, should_be_high_frequency=True)
	assert random_word_data != {}
	assert random_word_data.get("is_high_frequency_word") == True


