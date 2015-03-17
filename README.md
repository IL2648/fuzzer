# fuzzer
a web app fuzzer

# setup
In order to setup the fuzzer follow these instructions (using python 2.7 if possible)

1.) Follow the instructions to setup the local xampp instance <a href="http://yogi.se.rit.edu/~swen-331/activities/webapps.html">here</a>

2.) This is to download and install the "requests" library. Download the zip file for master from <a href="https://github.com/kennethreitz/requests">here</a>

3.) Unzip the file you just downloaded

4.) Open a command line and navigate to the folder you just unzipped

5.) Run the command <code>python setup.py install</code>

6.) This is to install the "Beautifulsoup" library. Download the zip file for master from <a href="https://github.com/bdoms/beautifulsoup">here</a>

7.) Unzip the file you just downloaded

8.) Open a command line and navigate to the folder you just unzipped

9.) Run the command <code>python setup.py install</code>

10.) Run fuzz script. Ensure you are using Python 2.7. Start with example script at the bottom. All output will automatically go to an "output.txt" file. 

Below is a description of the various options and how to use them.

fuzz [discover | test] url OPTIONS

  --custom-auth=string     Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa). Optional.

  Discover options:
    --common-words=file    Newline-delimited file of common words to be used in page guessing and input guessing. Required.

  Test options:
    --vectors=file         Newline-delimited file of common exploits to vulnerabilities. Required.

    --sensitive=file       Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. Required.

    --random=[true|false]  When off, try each input to each page systematically.  When on, choose a random page, then a random input field and test all vectors. Default: false.

    --slow=500             Number of milliseconds considered when a response is considered "slow". Default is 500 milliseconds

	NOTE: If the script is having trouble opening the files you pass in command line. Ensure any files you might path to (vectors, sensitive, or common-words) are located within the same directory as the fuzz script.

Example:

(WITH xampp app running already)
fuzz test http://127.0.0.1/ --custom-auth=dvwa --common-words=mywords.txt --vectors=vectors.txt --sensitive=sensitive.txt --random=False