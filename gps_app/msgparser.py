def __handle_subscription(message):
    result = []
    if 'models'in message:
        for k, v in message['models'].items():
            result.append([k, 'subscribed', v])
    if 'errors' in message:
        for k, v in message['collections'].items():
            result.append([k, 'subscribe failed', v])
    return result

def parse_message(message):
    if 'result' in message:
        return message['result']
    if 'message' in message:
        return message['message']
    elif 'error' in message:
        return message
    elif 'event' in message:
        channel = '.'.join(message['event'].split('.')[:-1])
        payload = message['data']['values']
        return [channel,payload]