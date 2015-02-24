import requests
import re

def parseURL(url, dict) :
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

#Testing using URLS taken from
dict = {}
dict = parseURL('http://simpply.se.rit.edu/Season/SeasonExplorer?sortColumn=Name&sortDescending=True&ActiveOnly=True', dict)
dict = parseURL('http://simpply.se.rit.edu/Season/SeasonExplorer?sortColumn=StartDate&sortDescending=False&ActiveOnly=True', dict)
dict = parseURL('http://simpply.se.rit.edu/Planogram/PlanogramExplorer?sortColumn=UnitsReceivedSeason&sortDescending=False&showActiveOnly=True', dict)
print dict
#This dictionary is keyed on the pages, with each entry being an input (which can be fuzzed)

#r = requests.get('http://simpply.se.rit.edu/Item/ItemDetail?itemId=100001')
#print r.content
