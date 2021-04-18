import json
import requests
from bs4 import BeautifulSoup as bs


def get_word_info(word):
	url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
	headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}
	request = requests.get(url, headers=headers)

	if request.status_code != 200:
		return {}

	soup = bs(request.text, "html.parser")
	info = soup.find(attrs={'class' : 'def-block'})

	if info:
		synonyms = []
		meaning, example = map(lambda x: x.strip(), info.text.strip().split(": "))
		if "Synonyms" in example:
			split = example.split(" Synonyms\n")
			example = split[0]
			synonyms = split[1].split("\n")
		return {
			"word" : word,
			"meaning" : meaning,
			"example" : example,
			"synonyms" : synonyms
		}
	return {}

class DB:
	def __init__(self, fp):
		self.fp = fp
		self.words = json.loads(open(fp, "r").read())

	def save(self):
		with open(self.fp, "w") as f:
			json.dump(self.words, f, indent=4)

	def add_word(self, word):
		self.words.append(word)
		self.save()
		return word

class Interface:
	class COLORS:
	    HEADER = '\033[95m'
	    OKBLUE = '\033[94m'
	    OKCYAN = '\033[96m'
	    OKGREEN = '\033[92m'
	    WARNING = '\033[93m'
	    FAIL = '\033[91m'
	    ENDC = '\033[0m'
	    BOLD = '\033[1m'
	    UNDERLINE = '\033[4m'

	def __init__(self, db):
		self.db = db


	def run(self):
		while True:
			word = input(Interface.COLORS.OKBLUE + "Please enter the word: " + Interface.COLORS.ENDC)
			word_info = get_word_info(word)
			if word_info:
				self.db.add_word(word_info)
				print ("WORD:" + Interface.COLORS.HEADER + word_info.get("word") + Interface.COLORS.ENDC)
				print ("MEANING:" + Interface.COLORS.OKCYAN + word_info.get("meaning") + Interface.COLORS.ENDC)
				print ("EXAMPLE:" + Interface.COLORS.OKGREEN + word_info.get("example") + Interface.COLORS.ENDC)
				print ("SYNONYMS:")
				if word_info.get("synonyms", None):
					for index, syn in enumerate(word_info.get("synonyms", None)):
						print (Interface.COLORS.OKBLUE + str(index + 1) + ". " + syn+ Interface.COLORS.ENDC)
			else:
				print (Interface.COLORS.FAIL  + "Word not found" + Interface.COLORS.ENDC)


if __name__ == '__main__':
	# print (get_word_info("impervious"))
	db = DB("words.json")
	interface = Interface(db)
	interface.run()

