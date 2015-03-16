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
	for k, v in formInputDict.items():
		url = k + "?"
		for e in v:
			url = url + e + "=<>\\\"&"
		start = int(round(time.time() * 1000))
		r = s.post(url)
		finish = int(round(time.time() * 1000))
		if(finish - start > slowTime):
			slowLog.append(url)
		isSanitized(r)
		checkResponse(r, e)

def checkURLs(s):
	for k, v in urlInputDict.items():
		url = k + "?"
		for e in v:
			url = url + e + "=<>\\\"&"
		start = int(round(time.time() * 1000))
		r = s.post(url)
		finish = int(round(time.time() * 1000))
		if(finish - start > slowTime):
			slowLog.append(url)
		isSanitized(r)
		checkResponse(r, e)

def isSanitized(r):
	if(r.url == bleach.clean(r.url)):
		print r.url + "=" + bleach.clean(r.url)
		return
	else:
		print r.url + "!=" + bleach.clean(r.url)
		unsanitized.append(r.url)
		return

def checkResponse(r, e):
    if( r.status_code >= 300 ):
        statusCodeLog.append((r.status_code,e))

with requests.Session() as s:
	sanitization(s)