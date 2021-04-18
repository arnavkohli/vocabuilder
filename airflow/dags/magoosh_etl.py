import os, json, pymongo

RAW_FILE_PATH = os.path.join(os.getcwd(), "../static/magoosh_raw_list.txt")


class Word:
	def __init__(self, word, type, meaning, example, is_high_frequency_word):
		self.word = word
		self.type = type
		self.meaning = meaning
		self.example = example
		self.is_high_frequency_word = is_high_frequency_word

	def json(self):
		return {
			"word" : self.word,
			"type" : self.type,
			"meaning" : self.meaning,
			"example" : self.example,
			"is_high_frequency_word": self.is_high_frequency_word
		}

def extract_to_dict(fp):
	raw_data = open(fp, "r").read()
	lines = raw_data.split("\n")
	skip = -1
	highFreqWord = True # first 300ish words are HFWs
	all_words = []
	for line_no, line in enumerate(lines):
		if line_no == skip:
			continue
		if 'Basic Words' == line.strip():
			highFreqWord = False
		elif '):' in line:
			line_split = line.split("):")
			word, type = line_split[0].split(" ")
			type = type[1:].strip()
			meaning = line_split[1].strip()
			all_words.append(Word(
					word=word,
					type=type,
					meaning=meaning,
					example=lines[line_no + 2],
					is_high_frequency_word=highFreqWord
				).json())
			skip = line_no + 2

	return all_words

if __name__ == '__main__':
	client = pymongo.MongoClient("mongodb+srv://arnav:t1WEjJ70xQg7ivWY@my-cluster.toozw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
	db = client.vocabuilder
	collection = db.new_magoosh_words
	data = extract_to_dict(RAW_FILE_PATH)
	collection.insert_many(data)







