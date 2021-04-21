import requests
from bs4 import BeautifulSoup as bs


def get_synonyms(word):
	url = f"https://www.google.com/search?q={word}+synonyms"
	headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}

	request = requests.get(url, headers=headers)
	if request.status_code != 200:
		print (request.text)
	else:
		print ("got 200")


	soup = bs(request.text, 'html.parser')

	divs = soup.find_all("div", attrs = {"role" : "list"})
	res = []
	for div in divs:
		spans = div.find_all("span")
		res += [span.text for span in spans]
	return res


if __name__ == '__main__':
	print (get_synonyms("aberrant"))


