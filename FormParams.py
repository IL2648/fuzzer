import requests
import re

#Dictionary is keyed on base URL (params stripped). The value of each key is a list containing all the values for the
#name attribute of each input for every form on that page
def parseHtmlForms(url, dict) :

    urlSplit = re.split("[=?&]",url)  #Split on URL params
    baseUrl = urlSplit[0]   #This is the base URL

    r = requests.get(url)
    inputElements = re.findall("<input.*?/>",r.content) #Find all "input" elements using a non-greedy regex

    for x in range(0, len(inputElements)):
        if "name=\"" in inputElements[x]: #Check to see if the result contains a "name" attribute
            inputName = re.findall("name=\"(.*?)\"", inputElements[x]) #Get a list that only contains the value of the "name" attribute
            print inputName

            if baseUrl in dict :  #If this URL is already in the dictionary...
                checkList = dict[baseUrl] #Put any already created params in a temp list
                if inputName not in checkList : #Check if item we're trying to add is in that temp list
                    dict[baseUrl].append(result[x])
            else :
                 dict[baseUrl] = inputName



    return dict

#Test with senior project site
dict = {}
parseHtmlForms('http://simpply.se.rit.edu/Item/ItemDetail?itemId=100001',dict)
print dict