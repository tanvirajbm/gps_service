import os
# import httplib
import http.client
import json
import oauth
import time
import msgparser
# import urllib2

nbi_label = "nbi"
nbi_host = os.environ[nbi_label+"_IP_ADDRESS"]
nbi_port = os.environ[nbi_label+"_TCP_8080_PORT"]

def get_config( ):
    print("Sending GET /api/v1/gps/config to %s:%s\n" % (nbi_host, nbi_port))
    print(oauth.access_token)
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "Authorization": "Bearer "+oauth.access_token
    }

    # con = httplib.HTTPConnection("%s:%s" % (nbi_host, nbi_port))
    con = http.client.HTTPConnection("%s:%s" % (nbi_host, nbi_port))
    con.request(
        "GET",
        "/api/v1/gps/config",
        None,
        headers
    )
    response = con.getresponse()
    msg=response.read().decode('utf8').replace("'", '"')
    parsed_message=msgparser.parse_message(json.loads(msg))
    print("Got Response %s %s\n\n" % (response.status, response.reason))
    print('Current config:\n')
    print(parsed_message)
    if response.status != 200 :
        print ("Failed to GET response")
        con.close()
        return None
    print ("Success")
    con.close()
    return response

def get_location( ):
    print("Sending GET /api/v1/gps/location to %s:%s\n" % (nbi_host, nbi_port))
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "Authorization": "Bearer "+oauth.access_token
    }

    # con = httplib.HTTPConnection("%s:%s" % (nbi_host, nbi_port))
    con = http.client.HTTPConnection("%s:%s" % (nbi_host, nbi_port))
    con.request(
        "GET",
        "/api/v1/gps/location",
        None,
        headers
    )
    response = con.getresponse()
    msg=response.read().decode('utf8').replace("'", '"')
    parsed_message=msgparser.parse_message(json.loads(msg))
    print("Got Response %s %s\n\n" % (response.status, response.reason))
    print('The current location of IR829 is\n')
    print(parsed_message)

    if response.status != 200 :
        print ("Failed to GET response")
        con.close()
        return None
    print ("Success")
    con.close()
    return response


   #payload = {"frequency" : 30}
   #con.request(
   #    "POST", 
   #     "/api/v1/random/model/config/set",
   #     json.dumps(payload),
   #     headers
   # )
   # response = con.getresponse()
   # print("%s %s %s" % (response.status, response.reason, response.read())) 
#
#    con.request(
#        "PUT", 
#        "/api/v1/random/model/config",
#        json.dumps(payload),
#        headers
#    )
#    response = con.getresponse()
#    print("%s %s %s" % (response.status, response.reason, response.read())) 
    
