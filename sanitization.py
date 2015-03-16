import requests
import time
urlInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
formInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
unsanitized = []
statusCodeLog = []
badChars = ["<",">","\"","\\"]
slowLog = []
slowTime = 50
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
        if(finish - start > slowTime):
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
        if(finish - start > slowTime):
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

with requests.Session() as s:
	sanitization(s)
	printSanitizationResults()
	print "\r\n\r\n\r\n"
	printResponseErrors()
	print "\r\n\r\n\r\n"
	printSlowResponses()
	print "\r\n\r\n\r\n"