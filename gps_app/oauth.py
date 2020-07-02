import os
import base64
#import urlparse
import urllib.parse
# import httplib
import http.client
import json
#from urllib import urlencode
from urllib.parse import urlencode
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

client_id = os.environ["OAUTH_CLIENT_ID"]
client_secret = os.environ["OAUTH_CLIENT_SECRET"]
server_ip = os.environ["OAUTH_TOKEN_SERVER_IPV4"]
server_port = os.environ["OAUTH_TOKEN_SERVER_PORT"]
api_path = os.environ["OAUTH_TOKEN_API_PATH"]
token_url = "https://"+server_ip+":"+server_port+api_path

print ("client_id: ",client_id)
print ("client_secret: ",client_secret)
print ("token_url: ",token_url)

# tokens = urlparse.urlparse(token_url)
tokens = urllib.parse.urlparse(token_url)
if tokens.scheme == 'https':
    # con = httplib.HTTPSConnection(tokens.netloc)
    con = http.client.HTTPSConnection(tokens.netloc)

else:
    # con = httplib.HTTPConnection(tokens.netloc)
    con = http.client.HTTPConnection(tokens.netloc)

x = client_id + ":" + client_secret
x_bytes = x.encode()
base64_bytes = base64.b64encode(x_bytes)
base64_message = base64_bytes.decode()
print (base64_message)

con.request(
    "POST",
    tokens.path,
    urlencode({'grant_type': 'client_credentials'}),
    {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + base64_message
    }
)

response = con.getresponse()
if response.status / 100 != 2:
    raise Exception("oauth token url returned %s" % response.status)

access_token = json.loads(response.read())['access_token']
con.close()
