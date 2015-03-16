import bleach
urlInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
formInputDict = {"https://www.google.com/webhp":["sourceid","ion","espv","ie"]}
unsanitized = []
def sanitization():
	checkForms()
	checkURLs()

def checkForms(s):
	for k,v in formInputDict:
		url = k + "?"
		for e in v:
			url = url + v + "=<>\\\"&"
		r = s.post(url)
		isSanitized(r)

def checkURLs(s):
	for k,v in urlInputDict:
		url = k + "?"
		for e in v:
			url = url + v + "=<>\\\"&"
		r = s.post(url)
		isSanitized(r)

def isSanitized(r):
	if(r.url == bleach.clean(r.url)):
		print r.url + "=" + bleach.clean(r.url)
		return
	else:
		print r.url + "!=" + bleach.clean(r.url)
		unsanitized.append(r.url)
		return
		
sanitization()