import json
import gps_client_api

def generate_data_to_visualizer(data):
    result_data={}
    message=json.loads(data[1]['message'])
    for feature in ["latitude","longitude"]:
        result_data[feature] = []
        if feature in message:
            value=message[feature]
            result_data[feature].append({"value":value})
    return result_data

def parse_message(message):
    if 'error' in message:
        return message
    elif 'message' in message:
        return message['message']
    elif 'event' in message:
        channel = '.'.join(message['event'].split('.')[:-1])
        payload = message['data']['values']
        data=[channel,payload]
        data_payload=generate_data_to_visualizer(data)
        print('Data format to be posted to visualizer',data_payload)
        post_gpsdata=gps_client_api.post_data_to_visualizer(data_payload,"datapoints")
        if post_gpsdata == None:
            print("POST request to post GPSdata to visualizer failed")
        return [channel,payload]