import sys
import requests
from collections import deque
import requests
from BeautifulSoup import *
import urlparse
import sys
import unicodedata

EXT = ('.doc', '.pdf', '.ppt', '.jpg', '.jpeg', '.png', '.gif', '.docx', '.pptx', '.tif', '.tiff', '.zip', '.rar', '.7zip', '.mov', '.ps', '.avi', '.mp3', '.mp4', '.txt', '.wav', '.midi')
links = []
explored = {}
urlInputs = []
words = []
auths = {
	'dvwa' : {
    	'username': 'admin',
    	'password': 'password',
    	'Login': 'Login'
	},
	'BodgeIt' : {
		'username': 'admin',
    	'password': 'password',
    	'Login': 'Login'
	}
}
args = {
	'mode' : '',
	'url' :	'',
	'customAuth' : False,
	'commonWords' : False
}

def main():
	args['mode'] = sys.argv[1]
	args['url'] = sys.argv[2]
	links.append(sys.argv[2])
	for arg in sys.argv:
		argval = arg.split("=")
		if(argval[0] == "--custom-auth"):
			args['customAuth']  = argval[1]
		if(argval[0] == "--common-words"):
			args['commonWords'] = argval[1]
	
	if(args['mode'] == 'discover'):
		with requests.Session() as s:
			if(args['customAuth']):
				s = auth(s)
		pageDiscovery(s)

def auth(s):
	if   (args['customAuth'] == 'dvwa'):
		s.post('http://127.0.0.1/dvwa/login.php', data=auths['dvwa'])
		return s
	elif (args['customAuth'] == 'BodgeIt'):
		return s
	print 'the custom authentication for ' + args['customAuth'] + ' does not exist'

def pageDiscovery(s):
	print("Running...")
	# For each link, find "children" links
	while len(links) > 0 :
		# get the next link
		url = links.pop(0)
		pageGuessing(s,url)
		explored[url] = 1
		# get "Child" links
		htmlLinks = linkDiscovery(s,url)
		# If the link isn't already in the queue and hasn't been looked at
		for link in htmlLinks :
			# If it's in the local domain... explore in detail later
			if htmlLinks[link] and link not in q and link not in explored :
				links.append(link)

def linkDiscovery(s,url):
	# Get, then parse the HTML source
    print "URL: " + url
    response = s.get(url)
    html = BeautifulSoup(response.text)
    print html
    # extract the links
    retVal = {}
    urlParts = urlparse.urlparse(url)
    for tag in html.find_all('a') :
        link = tag.get('href')
        if link is None :
            continue
        print "  " + link
        # Make the link a Fully Qualified Path (FQP)
        if link.startswith('/') :                           # Local
            link = urlParts[0] + '://' + urlParts[1] + link
        elif link.startswith('#') :                         # Bookmark
            #link = urlParts[0] + '://' + urlParts[1] + urlParts[2] + link
            # I don't want bookmarks, they are on the same page as the current url
            continue
        elif not link.startswith('http') :                  # External or Local w/ FQP
            link = urlParts[0] + '://' + urlParts[1] + '/' + link        

        # Add the link, set 1 if in domain and not a "file"
        if urlParts[1] == urlparse.urlparse(str(link))[1] and not link.lower().endswith(EXT) :
            retVal[link] = 1
        else :
            retVal[link] = 0

    return retVal

def pageGuessing(s,url):
    print('Running page guessing...')

    #Read the list of commond words
    with open(args['commonWords']) as f:
        if(f):
            wordList = f.read().splitlines()

    pages = []
    for URL in links:
        slashCount = URL.count('/')
        URL2=''
        for char in URL:
            if slashCount == 0:
                break
            if char == '/':
                slashCount=slashCount-1
            URL2 += char

        for word in wordList:
            for extension in EXT:
                newURL = URL2+word+extension
                r = requests.get(newURL)
                if r.status_code == 200:
                    pages.append(newURL)
                    print(newURL)
    return pages

def inputDiscovery(s,url):
	return

def parseURLs(s,url):
	return

def formParameters(s,url):
	return

def cookies(s,url):
	return

main()