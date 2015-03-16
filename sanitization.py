import bleach
import requests
import time
urlInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
formInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
unsanitized = []
statusCodeLog = []
slowLog = []
slowTime = 500
def sanitization(s):
	checkForms(s)
	checkURLs(s)

def checkForms(s):
	for k,v in formInputDict:
		url = k + "?"
		for e in formInputDict[v]:
			url = url + e + "=<>\\\"&"
		start = lambda: int(round(time.time() * 1000))
		r = s.post(url)
		finish = lambda: int(round(time.time() * 1000))
		if(finish - start > slowTime):
			slowLog.append(url)
		isSanitized(r)
		checkResponse(r)

def checkURLs(s):
	for k in urlInputDict:
		url = k + "?"
		for e in urlInputDict[v]:
			url = url + e + "=<>\\\"&"
		start = lambda: int(round(time.time() * 1000))
		r = s.post(url)
		finish = lambda: int(round(time.time() * 1000))
		if(finish - start > slowTime):
			slowLog.append(url)
		isSanitized(r)
		checkResponse(r)

def isSanitized(r):
	if(r.url == bleach.clean(r.url)):
		print r.url + "=" + bleach.clean(r.url)
		return
	else:
		print r.url + "!=" + bleach.clean(r.url)
		unsanitized.append(r.url)
		return

def checkResponse(r):
    if( r.status_code >= 300 ):
        statusCodeLog.append((r.status_code,newURL))

with requests.Session() as s:
	sanitization(s)