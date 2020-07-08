import os
# import httplib
import http.client
import json
import oauth
import time
import msgparser
import ssl
# import urllib2

nbi_label = "nbi"
nbi_host = os.environ[nbi_label+"_IP_ADDRESS"]
nbi_port = os.environ[nbi_label+"_TCP_8080_PORT"]
iox_ip = os.getenv("DATASTORE_SERVER_IPV4")
iox_port = os.getenv("DATASTORE_SERVER_PORT")
iox_token = os.getenv("IOX_TOKEN")
iox_app_id = os.getenv("CAF_APP_ID")

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
    if response.status != 200 :
        print ("Failed to GET response")
        con.close()
        return None
    msg=response.read().decode('utf8').replace("'", '"')
    parsed_message=msgparser.parse_message(json.loads(msg))
    print("Got Response %s %s\n\n" % (response.status, response.reason))
    print('The current location of IR829 is\n')
    print(parsed_message)
    print ("Success")
    con.close()
    return response

def post_data_to_visualizer(payload, endpoint):
    print('Data content being posted to visualizer is',payload)                                                        
    con = http.client.HTTPSConnection(iox_ip, iox_port, timeout=20)     
    content = json.dumps(payload)
    headers = {"Content-Type": "application/json", "X-Token-Id": iox_token, "X-App-Id": iox_app_id}
    print('Header is', headers)                                
    url = "/iox/api/v2/hosting/apps/" + iox_app_id + "/ioxv/" + endpoint                
    print('URL IS',url)                                                                 
    con.request("PUT", url, content, headers)                                                  
    time.sleep(2)                                                                       
    response = con.getresponse()                                                                                               
    if response.status != 200 :                                                                    
        print("Failed to post data to visualizer %s:%s",response.status,response.reason)           
        con.close()                                                                                
        return None                                                                                
    print("SUCESSS: Data posted to visualizer")                                                    
    con.close()                                                                                    
    return response