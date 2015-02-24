import sys
import requests

def main():

	#execute page guessing function
	pageGuassingList = pageGuessing()
	print("The list of the unlinked pages:")
	for page in pageGuassingList:
		print(page)
	
	#execute discovering cookie function
	cookies = readCookies()
	print("The cookies of the website :")
	print(cookies)
		
def pageGuessing():

	#Read the url list.
	with open('docs/URLList.txt') as f:
		URLList = f.read().splitlines()

	#Read the url extensions
	with open('docs/extensionList.txt') as f:
		URLExtensionList = f.read().splitlines()
	
	#Read the word list of 
	wordsListFileName = sys.argv[3][15:]
	with open('docs/'+ wordsListFileName) as f:
		wordList = f.read().splitlines()
	pages = []
	
	for URL in URLList:
		slashCount = URL.count('/')
		for char in URL:
			if slashCount == 0:
				break
			if x == '/':
				i=i-1
			URL2 += char
		
		for word in wordList:
			for extension in URLExtensionList:
				newURL = URL2+word+extension
				r = requests.get(newURL)
				if r.status_code == 200:
					pages.append(newURL)
	return pages
	
def readCookies():
	r = requests.Session()
	r.get(sys.argv[2])
	return r.cookies
	
if __name__ == "__main__":
	main()