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

        urlInputDict ={}
        formInputDict={}
        pageDiscovery(s,urlInputDict,formInputDict)
        inputDiscoveryPrinting(urlInputDict, formInputDict)
        pageGuessing(s)
        print cookies(s)

def auth(s):
	if   (args['customAuth'] == 'dvwa'):
		s.post('http://127.0.0.1/dvwa/login.php', data=auths['dvwa'])
		return s
	elif (args['customAuth'] == 'BodgeIt'):
		return s
	print 'the custom authentication for ' + args['customAuth'] + ' does not exist'

def pageDiscovery(s, urlInputDict, formInputDict):
    print("Running...")
	# For each link, find "children" links
    while len(links) > 0 :
        # get the next link
        url = links.pop(0)
        explored[url] = 1
        # get "Child" links
        htmlLinks = linkDiscovery(s,url)
        parseURL(s,url,urlInputDict)
        formParameters(s,url, formInputDict)
        # If the link isn't already in the queue and hasn't been looked at
        for link in htmlLinks :
            # If it's in the local domain... explore in detail later
            if htmlLinks[link] and link not in links and link not in explored :
                links.append(link)
                explored[link] = 0

def linkDiscovery(s,url):
	# Get, then parse the HTML source
    print "URL: " + url
    #pageGuessing(s,url)
    response = s.get(url)
    html = BeautifulSoup(response.text)
    # extract the links
    retVal = {}
    urlParts = urlparse.urlparse(url)
    for tag in html.findAll('a') :
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

def pageGuessing(s):
    print('Running page guessing...')

    #Read the list of commond words
    with open(args['commonWords']) as f:
        if(f):
            wordList = f.read().splitlines()

    pages = []
    for URL in explored.keys():
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
                r = s.get(newURL)
                if r.status_code == 200:
                    pages.append(newURL)
                    print(newURL)
    return pages

def inputDiscoveryPrinting(urlParsingDict, formParsingDict):
    print "***Inputs parsed through URLS***"
    for k,v in urlParsingDict.iteritems():
        print k + ":"
        for x in range(0, len(v)):
            print "    " + v[x]

    print "***Input Field Names from Forms***"
    for k,v in formParsingDict.iteritems():
        print k + ":"
        for x in range(0, len(v)):
            print "    " + v[x]
	return

def parseURL(s, url, dict) :
    print "parsing..."
    print
    result = re.split("[=?&]",url)  #Split on URL params

    for x in range(1, len(result)) :  #Iterate through each split item
        if(x % 2 ==1) :     #If the item is odd, then it is a param

            if result[0] in dict :  #If this URL is already in the dictionary...
                checkList = dict[result[0]] #Put any already created params in a temp list
                if result[x] not in checkList : #Check if item we're trying to add is in that temp list
                    dict[result[0]].append(result[x])
            else :
                dict[result[0]] = [result[x]]
        x+=1

    return dict

def formParameters(s, url, dict):

    urlSplit = re.split("[=?&]",url)  #Split on URL params
    baseUrl = urlSplit[0].encode("ascii")   #This is the base URL

    r = requests.get(url)
    inputElements = re.findall("<input.*?/>",r.content) #Find all "input" elements using a non-greedy regex

    for x in range(0, len(inputElements)):
        if "name=\"" in inputElements[x]: #Check to see if the result contains a "name" attribute
            inputName = re.findall("name=\"(.*?)\"", inputElements[x]) #Get a list that only contains the value of the "name" attribute
            inputName = inputName.pop()
            if baseUrl in dict :  #If this URL is already in the dictionary...
                checkList = dict[baseUrl] #Put any already created params in a temp list
                if inputName not in checkList : #Check if item we're trying to add is in that temp list
                    dict[baseUrl].append(inputName)
            else :
                 dict[baseUrl] = [inputName]
    return dict

def cookies(s):
	return s.cookies

main()