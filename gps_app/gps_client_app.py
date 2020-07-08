import websocket
import json
import gps_client_api
import msgparser
import sys
import oauth
import time
import ssl
import os

id = 1
sub = False

metadata_payload = {
  "datapoints": {
    "latitude": {
      "units": "",
      "displayName": "Latitude",
      "graphType": "table",
    },
    "longitude": {
      "units": "",
      "displayName": "Longitude",
      "graphType": "table",
    }
  }
}

def subscribe(ws):
    global id
    id = id+1
    msg = {"id":id, "method":"subscribe.{}".format('gps.stream') }
    ws.send(json.dumps(msg))

def unsubscribe(ws):
    global id
    id = id+1
    msg = {"id":id, "method":"unsubscribe.{}".format('gps.stream') }
    ws.send(json.dumps(msg))

def on_open(ws):
    global id
    print("opened")
    msg = {"id":id,"method":"auth.{}".format('auth.oauth')}
    ws.send(json.dumps(msg))

def on_message(ws, message):
    global sub
    # print('message received from resgate server: ', message)
    #msg=msgparser.parse_message(json.loads(message))
    #print('Parsed message is',msg)
    if not sub:
       print("Calling Subscribe")
       subscribe(ws)
       sub = True
    msg=msgparser.parse_message(json.loads(message))
    print('message received from resgate server: ', msg)

def on_error(ws, error):
    print('There was an error {}'.format(error))

def on_close(ws):
    print("closed")

if __name__ == '__main__':
    nbi_label = "nbi"
    nbi_host = os.environ[nbi_label+"_IP_ADDRESS"]
    nbi_port = os.environ[nbi_label+"_TCP_8080_PORT"]


    time.sleep(10)
    config = gps_client_api.get_config()
    if config == None :
        print("GET config Request failed")
        sys.exit(0)
    time.sleep(10)
    location = gps_client_api.get_location()
    if location == None :
        print("GET location Request failed")
        sys.exit(0)
    time.sleep(10)
    websocket.enableTrace(True)
    url = "ws://%s:%s" % (nbi_host, nbi_port)

    #Post meta data
    post_metadata=gps_client_api.post_data_to_visualizer(metadata_payload,"metadata")
    if post_metadata == None:
        print("POST request to post metadata to visualizer failed")
    ws = websocket.WebSocketApp(url,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open=on_open,
                                header = ["Authorization: Bearer " + oauth.access_token])

    ws.run_forever(sslopt = {"cert_reqs": ssl.CERT_NONE})