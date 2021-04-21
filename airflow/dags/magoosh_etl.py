from pprint import pprint 
import os, json, pymongo, requests
from bs4 import BeautifulSoup as bs

RAW_FILE_PATH = os.path.join(os.getcwd(), "../static/magoosh_raw_list.txt")

def get_word_info(word):
	print (word)
	url = f"https://www.google.com/search?q={word}+meaning"
	headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}

	request = requests.get(url, headers=headers)
	if request.status_code != 200:
		print (request.text)
	else:
		print ("got 200")

	soup = bs(request.text, 'html.parser')

	boxes = soup.find_all("div", attrs = {"class" : "L1jWkf h3TRxf"})

	if len(boxes) == 0:
		return {}


	count = 0
	while True:
		try:
			box = boxes[count]
			meanings = []
			examples = []
			all_synonyms = []

			# for box in boxes:
			divs = box.find_all("div")

			meaning = divs[0].text
			meanings.append(meaning)

			example = divs[1].text
			examples.append(example)

			try:
				synonyms = [i.text.strip() for i in divs[3].find_all("span") if i.text.strip() != ""]
				all_synonyms += synonyms
			except:
				synonyms = [i.text.strip() for i in divs[2].find_all("span") if i.text.strip() != ""]
				all_synonyms += synonyms
			
			return {
				"word" : word,
				"meanings" : meanings,
				"examples" : examples,
				"synonyms" : all_synonyms
			}
		except:
			continue
		count += 1
		if count == 5:
			break

	return {}

class Word:
	def __init__(self, word, type, meaning, examples, is_high_frequency_word, synonyms):
		self.word = word
		self.type = type
		self.meaning = meaning
		self.examples = examples
		self.is_high_frequency_word = is_high_frequency_word
		self.synonyms = synonyms

	def json(self):
		return {
			"word" : self.word,
			"type" : self.type,
			"meanings" : self.meaning,
			"examples" : self.examples,
			"is_high_frequency_word": self.is_high_frequency_word,
			"synonyms" : self.synonyms
		}

def get_synonyms_and_examples_from_thesaurus(word):
	url = f"https://www.thesaurus.com/browse/{word}"
	headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}

	request = requests.get(url, headers=headers)
	if request.status_code != 200:
		print ("got not 200")
	else:
		print (word)

	soup = bs(request.text, 'html.parser')

	div = soup.find("div", attrs = {"id" : "meanings"})
	
	try:
		synonyms = [i.text for i in div.find_all("li")[:5]]
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

def extract_to_dict(fp):
	raw_data = open(fp, "r").read()
	lines = raw_data.split("\n")
	skip = -1
	highFreqWord = True # first 300ish words are HFWs
	all_words = []
	total_lines = len(lines)
	for line_no, line in enumerate(lines):
		if line_no == skip:
			continue
		if 'Basic Words' == line.strip():
			highFreqWord = False
			# Early stoppage for HFWs
			break
		elif '):' in line:
			line_split = line.split("):")
			word, type = line_split[0].split(" ")
			synonyms, examples = get_synonyms_and_examples_from_thesaurus(word)

			meaning = line_split[1].strip()

			try:
				all_words.append(Word(
					word=word,
					type=type,
					meaning=meaning,
					examples=[lines[line_no + 2]] + examples,
					is_high_frequency_word=highFreqWord,
					synonyms=synonyms
				).json())

				skip = line_no + 2
				print (f"[{line_no + 1} / {total_lines}] ")
				# pprint (all_words)
				# break
			except Exception as err:
				print (err)
				print (f"skipping {word}")
	return all_words

if __name__ == '__main__':
	client = pymongo.MongoClient("mongodb+srv://arnav:t1WEjJ70xQg7ivWY@my-cluster.toozw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
	db = client.vocabuilder
	collection = db.new_magoosh_words
	data = extract_to_dict(RAW_FILE_PATH)
	with open("data.json", "w") as f:
		json.dump(data, f, indent=4)
	collection.insert_many(data)
	# print (get_word_info("concede"))
	# extract_to_dict(RAW_FILE_PATH)
	# pprint (get_synonyms_and_examples_from_thesaurus("abstain"))






