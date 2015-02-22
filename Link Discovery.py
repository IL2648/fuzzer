from collections import deque
import requests
from bs4 import BeautifulSoup
import urlparse
import sys
import unicodedata
EXT = ('.doc', '.pdf', '.ppt', '.jpg', '.jpeg', '.png', '.gif', '.docx', '.pptx', '.tif', '.tiff', '.zip', '.rar', '.7zip', '.mov', '.ps', '.avi', '.mp3', '.mp4', '.txt', '.wav', '.midi')

# Finds links on a page
# returns a dictionary with the link as a Key and 1 for Internal or 0 for External
def findLinks(url) :
    # Get, then parse the HTML source
    print "URL: " + url
    response = requests.get(url)
    html = BeautifulSoup(response.text)

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


def scrapeURL(root) :
    print("Running...")
    print
    q = deque([root])
    explored = {}
    try :
        # For each link, find "children" links
        while len(q) > 0 :
            # get the next link
            url = q.popleft()
            explored[url] = 1
            # get "Child" links
            htmlLinks = findLinks(url)
            # If the link isn't already in the queue and hasn't been looked at
            for link in htmlLinks :
                # If it's in the local domain... explore in detail later
                if htmlLinks[link] and link not in q and link not in explored :
                    q.append(link)
                # If it's not in the local domain, we will not explore and say we did
                elif (htmlLinks[link] == 0) and link not in explored :
                    explored[link] = 1
    except KeyboardInterrupt :
        pass
    return explored


# **********************************************************************
# **********************************************************************
# **************************** Main ************************************
# **********************************************************************
# **********************************************************************

def main() :
    INPUT_URL = "http://www.cs.rit.edu"

    # Parse the html for hyperlinks
    allLinks = scrapeURL(INPUT_URL)

    # Print the results
    print("LINKS DISCOVERED:")
    for link in allLinks :
        print(link)
    return


if __name__ == "__main__":
    main()