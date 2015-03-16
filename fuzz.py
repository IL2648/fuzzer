import re
import os
import sys
import requests
from collections import deque
import requests
from bs4 import BeautifulSoup
import urlparse
import sys
import unicodedata
# Comments Regarding imports
#
# For some reason I (Geoff) need to import re
#   for the program to not give an import error
#
# This is the BeautifulSoup I (Geoff) have, it's 
#   the newest version but if we're using the older 
#   version for submission we can just change this
#   to 'from BeautifulSoup import *''


EXT = (
    '.doc', '.pdf', '.ppt', '.jpg', '.jpeg', '.png', '.gif', '.docx', '.pptx', '.tif', '.tiff', '.zip',
    '.rar', '.7zip', '.mov', '.ps', '.avi', '.mp3', '.mp4', '.txt', '.wav', '.midi')
links = []
explored = {}
urlInputs = []
urlInputDict = {}
formInputDict = {}
words = []
unsanitized = []
statusCodeLog = []
badChars = ["<",">","\"","\\"]
slowLog = []
BaseUrl = ''
TO_FILE = True
logFile = open('output.txt', 'w')
auths = {
    'dvwa': {
        'username': 'admin',
        'password': 'password',
        'Login': 'Login'
    },
    'BodgeIt': {
        'username': 'admin',
        'password': 'password',
        'Login': 'Login'
    }
}
args = {
    'mode': '',
    'url': '',
    'customAuth': False,
    'commonWords': False,
    'vectors': '',
    'sensitive': '',
    'random': False,
    'slow': 500
}

def main():
    # ensure that we have at least the bare minimum of arguments
    if (sys.argv.__len__() < 2):
        output("Not enough arguments, you must have at least 2, please follow this format")
        output("fuzz [discover | test] url OPTIONS")
        sys.exit()

    #Ensure first argument is what it's supposed to be
    args['mode'] = sys.argv[1]
    if ((args['mode'] != 'discover') & (args['mode'] != 'test')):
        output("The mode is set to [" + args['mode'] + "] Please set it to discover or test")
        sys.exit()

    links.append(sys.argv[2])

    #Parse through options
    for arg in sys.argv:
        argval = arg.split("=")
        if (argval[0] == "--custom-auth"):
            args['customAuth'] = argval[1]
        elif (argval[0] == "--common-words"):
            args['commonWords'] = argval[1]
        elif (argval[0] == "--vectors"):
            args['vectors'] = argval[1]
        elif (argval[0] == "--sensitive"):
            args['sensitive'] = argval[1]
        elif (argval[0] == "--random"):
            args['random'] = argval[1]
        elif (argval[0] == "--slow"):
            args['slow'] = argval[1]

    args['url'] = sys.argv[2]
    with requests.Session() as s:
        if (args['customAuth']):
            s = auth(s)

        #Test the URL to make sure we can get something from it. Exit with grace.
        try:
            s.get(args['url'])
        except requests.exceptions.ConnectionError:
            output("Connection could not be established to designated URL")
            sys.exit()

    # Run program
    pageDiscovery(s)
    inputDiscoveryPrinting(urlInputDict, formInputDict)
    pageGuessing(s)

    # Close the log file
    logFile.close()


def auth(s):
    if   (args['customAuth'] == 'dvwa'):
        s.post('http://127.0.0.1/dvwa/login.php', data=auths['dvwa'])
        return s
    elif (args['customAuth'] == 'BodgeIt'):
        return s
    output('the custom authentication for ' + args['customAuth'] + ' does not exist')


# This function will start by finding links for the base URL provided 
#   in the args.  Each link (found in an <a href> tag) will be added to
#   a list of possible links to explore provided it has not already
#   been explored.  Once all links from all depths within the base URL
#   domain are scraped, the function is complete.
# In addition, the URL is parsed for each URL explored while the link
#   discovery is running
# In addition, the URL is parsed for form information in each URL
#   explored while the link discovery is running.
# NOTES: 
# The list of links scraped only includes those links that
#   permitted by the linkDiscovery() function which is determined
#   by looking at the value in the dictionary (1=check, 0=skip)
def pageDiscovery(s):
    output("***Fuzzing " + links[0] + "***\n")
    # For each link, find "children" links
    while len(links) > 0:
        # get the next link
        url = links.pop(0)
        explored[url] = 1
        output("Fuzz results for " + url)

        # connect to this link, if there is an error, skip it.
        try:
            response = s.get(url)
        except:
            output("    An error occurred attempting to connect to " + url + "\n")
            continue

        # check the response for sensitive data if the arg was used
        if args['sensitive']:
            findings = checksensitivedata(response)

            # Print sensitive word results
            if findings is not None:
                for word in findings.keys():
                    output("      " + word + " - " + str(findings[word]))
            else:
                output("      < none >")
            output("")

        # Parse the URL for parameters
        parseURL(s, url, urlInputDict)

        # Check the page for input fields/forms
        formParameters(s, url, formInputDict)

        # Scrape links from this page
        htmlLinks = linkDiscovery(url, response)

        # If no links were returned, try the next url
        output("    ***Links Discovered***")
        if htmlLinks is None:
            output("      < none >")
            output("")
            continue
        # If the link isn't already in the queue and hasn't been looked at
        for link in htmlLinks:
            output("      " + link)
            # If it's in the local domain... explore in detail later
            if htmlLinks[link] and link not in links and link not in explored:
                links.append(link)
                explored[link] = 0
        output("")


# This function scrapes hyperlinks from the URL provided, it then analyzes
#   those links, provided they are not a type of file and that the link is
#   not one that has already been scraped it is added to a list which will 
#   be scraped later and analyzed in the same manner.
# In addition, this function checks the response for sensitive data if the
#   argument was provided.  This was an effort to avoid calling response
#   again later in the program and just using it as soon as it was received.
def linkDiscovery(url, response):
    # extract the links
    html = BeautifulSoup(response.text)
    retVal = {}
    urlParts = urlparse.urlparse(url)
    for tag in html.findAll('a'):
        link = tag.get('href')
        link = link.rstrip('.') #remove all trailing periods
        if link is None:
            continue
        # Make the link a Fully Qualified Path (FQP)
        if link.startswith('/'):  # Local
            link = urlParts[0] + '://' + urlParts[1] + link
        elif link.startswith('#'):  # Bookmark
            #link = urlParts[0] + '://' + urlParts[1] + urlParts[2] + link
            # I don't want bookmarks, they are on the same page as the current url
            continue
        elif link.startswith('../') : #Strange infinite loop case which came up during http://127.0.0.1/dvwa/ test
            continue
        elif not link.startswith('http'):  # External or Local w/ FQP
            #link = BaseUrl + link #when using the url parser to build, this was building incorrectly for http://127.0.0.1/dvwa/
            link = urlParts[0] + '://' + urlParts[1] + '/' + link
            #Putting the "Broken" code back in, just in case I'm wrong and it was fine.
        # else:
        #     # Assume that it is a good link missing the / because that form is still valid.
        #     link = urlParts[0] + '://' + urlParts[1] + "/" + link

        # Add the link, set 1 if in domain and not a "file"
        if urlParts.hostname == urlparse.urlparse(str(link)).hostname and not link.lower().endswith(EXT):
            retVal[link] = 1
        else:
            retVal[link] = 0

    return retVal


def pageGuessing(s):
    # check if the page guessing arg exists, if not, return
    if (args['commonWords'] == False):
        return
    output('Running page guessing...')

    privateEXT = EXT + ('.php', '.html')

    # Read the list of commond words
    with open(args['commonWords']) as f:
        if (f):
            wordList = f.read().splitlines()

    pages = []
    for URL in explored.keys():
        output("guessing for " + URL)
        slashCount = URL.count('/')
        URL2 = ''
        for char in URL:
            if slashCount == 0:
                break
            if char == '/':
                slashCount = slashCount - 1
            URL2 += char

        for word in wordList:
            for extension in privateEXT:
                newURL = URL2 + word + extension
                r = s.get(newURL)
                if r.status_code < 300:
                    pages.append(newURL)
                    output(newURL)
                #else:
                    #statusCodeLog.append((r.status_code,newURL))
    return pages


def inputDiscoveryPrinting(urlParsingDict, formParsingDict):
    output("***Inputs parsed through URLS***")
    for k, v in urlParsingDict.iteritems():
        output(k + ":")
        for x in range(0, len(v)):
            output("    " + v[x])

    output("***Input Field Names from Forms***")
    for m, n in formParsingDict.iteritems():
        output(m + ":")
        for y in range(0, len(n)):
            output("    " + n[y])


def parseURL(s, url, dict):
    output("    ***Parameters Discovered***")
    output("")
    result = re.split("[=?&]", url)  # Split on URL params

    for x in range(1, len(result)):  # Iterate through each split item
        if (x % 2 == 1):  # If the item is odd, then it is a param

            if result[0] in dict:  #If this URL is already in the dictionary...
                checkList = dict[result[0]]  #Put any already created params in a temp list
                if result[x] not in checkList:  #Check if item we're trying to add is in that temp list
                    dict[result[0]].append(result[x])
            else:
                dict[result[0]] = [result[x]]
        x += 1

    return dict


def formParameters(s, url, dict):
    urlSplit = re.split("[=?&]", url)  # Split on URL params
    baseUrl = urlSplit[0].encode("ascii")  # This is the base URL

    r = s.get(url)
    inputElements = re.findall("<input.*?>", r.text)  # Find all "input" elements using a non-greedy regex

    for x in range(0, len(inputElements)):
        if "name=\"" in inputElements[x]:  # Check to see if the result contains a "name" attribute
            inputName = re.findall("name=\"(.*?)\"",
                                   inputElements[x])  # Get a list that only contains the value of the "name" attribute
            inputName = inputName.pop()
            if baseUrl in dict:  # If this URL is already in the dictionary...
                checkList = dict[baseUrl]  #Put any already created params in a temp list
                if inputName not in checkList:  #Check if item we're trying to add is in that temp list
                    dict[baseUrl].append(inputName)
            else:
                dict[baseUrl] = [inputName]
    return dict


def cookies(s):
    return s.cookies


def checksensitivedata(response):
    output("    ***Sensitive Data***")
    # Get sensitive data from file
    with open(args['sensitive']) as f:
        if (f):
            sensitiveWords = f.read().splitlines()

    retVal = {}
    # For every sensitive word, see if it's in the response
    for word in sensitiveWords:
        count = len(re.findall(r"\b" + word + r"\b", response.text, re.IGNORECASE))      # Find all whole words
        if count:
            retVal[word] = count

    return retVal

# Use in place of print to also use a log file
def output(msg):
    global TO_FILE
    if TO_FILE:
        logFile.write(msg)
        logFile.write("\n")
    print(msg)

def checkResponse(r):
    if( r.status_code >= 300 ):
        statusCodeLog.append((r.status_code,newURL))

currentMilliTime = lambda: int(round(time.time() * 1000))
def sanitization(s):
    checkForms(s)
    checkURLs(s)

def checkForms(s):
    for k, v in formInputDict.items():
        url = k + "?"
        for e in v:
            url = url + e + "=<>\\\"&"
        start = currentMilliTime()
        r = s.post(url)
        finish = currentMilliTime()
        if(finish - start > args["slow"]):
            slowLog.append((url,finish-start))
        isSanitized(r)
        checkResponse(r)

def checkURLs(s):
    for k, v in urlInputDict.items():
        url = k + "?"
        for e in v:
            url = url + e + "=<>\\\"&"
        start = currentMilliTime()
        r = s.get(url)
        finish = currentMilliTime()
        if(finish - start > args['slow']):
            slowLog.append((url,finish-start))
        isSanitized(r)
        checkResponse(r)

def isSanitized(r):
    for e in badChars:
        if e in r.url:
            unsanitized.append(r.url)
            break

def checkResponse(r):
    if( r.status_code >= 300 ):
        statusCodeLog.append((r.status_code,r.url))

def printSanitizationResults():
    print "-----------------------------------------------"
    print "----------------UNSANITIZED URLs---------------"
    print "-----------------------------------------------"
    for e in unsanitized:
        print e
        print "-----------------------------------------------"
    print "------------END OF UNSANITIZED URLs------------"
    print "-----------------------------------------------"

def printResponseErrors():
    print "-----------------------------------------------"
    print "-----------------HTTP ERRORS-------------------"
    print "-----------------------------------------------"
    for c,u in statusCodeLog:
        print "("+str(c)+" : "+u+")"
        print "-----------------------------------------------"
    print "-------------END OF HTTP ERRORS----------------"
    print "-----------------------------------------------"

def printSlowResponses():
    print "-----------------------------------------------"
    print "-----------------SLOW RESPONSES----------------"
    print "-----------------------------------------------"
    for u,t in slowLog:
        print "("+str(t)+" : "+u+")"
        print "-----------------------------------------------"
    print "---------------END OF SLOW RESPONSES-----------"
    print "-----------------------------------------------"
main()