import requests
import time
urlInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
formInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
unsanitized = []
statusCodeLog = []
badChars = ["<",">","\"","\\"]
slowLog = []
slowTime = 500
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
			slowLog.append(url)
		isSanitized(r)
		checkResponse(r, e)

def checkURLs(s):
	for k, v in urlInputDict.items():
		url = k + "?"
		for e in v:
			url = url + e + "=<>\\\"&"
		start = currentMilliTime()
		r = s.post(url)
		finish = currentMilliTime()
		if(finish - start > slowTime):
			slowLog.append(url)
		isSanitized(r)
		checkResponse(r, e)

def isSanitized(r):
	for e in badChars:
		if e in r.url:
			print "unsanitary"
			unsanitized.append(r.url)
			break
	print "sanitary"

def checkResponse(r, e):
    if( r.status_code >= 300 ):
        statusCodeLog.append((r.status_code,e))

with requests.Session() as s:
	sanitization(s)