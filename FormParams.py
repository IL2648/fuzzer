import requests

r = requests.get('http://simpply.se.rit.edu/Item/ItemDetail?itemId=100001')
print r.content