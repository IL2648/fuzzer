import requests
from requests.auth import HTTPBasicAuth
import sys
# Fill in your details here to be posted to the login form.
auths = { 
'dvwa' : {
    'username': 'admin',
    'password': 'password',
    'Login': 'Login'
}, 

}

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    r = s.post('http://127.0.0.1/dvwa/login.php', data=payload)
    # print the html returned or something more intelligent to see if it's a successful login page.
    print r.text
    r = s.get('http://127.0.0.1/dvwa/login.php');
    print r.text
    r = s.get('http://127.0.0.1/dvwa/index.php');
    print r.text
for arg in sys.argv:
	argval = arg.split("=")
	if(len(argval) == 1):
		if(argval[0] == "test"):
			mode = "test"
		elif(argval[0] == "discover"):
			mode = "discover"
		else:
			url = argval
	if(argval[0] == "--custom-auth"):
		customAuth = argval[1]
	if(argval[0] == "--common-words"):
		commonWords = argval[1]
	if(argval[0] == "--vectors"):
		vectors = argval[1]
	if(argval[0] == "--sensitive"):
		sensitive = argval[1]
	if(argval[0] == " --random"):
		random = argval[1]
	if(argval[0] == "--slow"):
		slow = argval[1]
