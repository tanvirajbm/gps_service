import asyncio
import os
import json
import pynmea2
import io
import copy
from nats.aio.client import Client as NATS
from configparser import SafeConfigParser


loop = asyncio.get_event_loop()
count = 0
subscriptions = dict()
gps_data={}
current_gps_data={}
gps_interval_sec=5
topic='gps.stream'

#Get hold of the configuration file (package_config.ini)
moduledir = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.getenv("CAF_APP_PATH", moduledir)
tcfg = os.path.join(BASEDIR,  "package_config.ini")
CONFIG_FILE = os.getenv("CAF_APP_CONFIG_FILE", tcfg)
cfg = SafeConfigParser()
cfg.read(CONFIG_FILE)

def set_gps_interval_sec():
    global cfg
    global gps_interval_sec
    for section in ['gps-config']:
        for options in ['interval']:
            if cfg.has_section(section) and cfg.has_option(section, options):
                #Read interval from package_config.ini only if the section interval exists in the file
                gps_interval_sec=cfg.getint("gps-config","interval")
            else:
                gps_interval_sec=5

def format_timestamp(timeval,dateval):
    formatted_time = str(dateval.strftime("%a %b %d "))+str(timeval)+str(dateval.strftime(" %Y"))
    return formatted_time

def parse_data(msg):
    global gps_data

    latitude=msg.lat
    longitude=msg.lon
    altitude=msg.altitude
    # timestamp=format_timestamp(msg.timestamp,msg.datestamp)
    timestamp=str(msg.timestamp)

    gps_data['latitude']=latitude
    gps_data['longitude']=longitude
    gps_data['timestamp']=timestamp
    gps_data['altitude']=altitude

async def run(loop):
    #global gps_interval_sec
    nc = NATS()
    url=os.environ.get("message_broker_IP_ADDRESS")+":"+os.environ.get("message_broker_TCP_4222_PORT")
    await nc.connect(url,loop=loop)

    #Set the variable gps_interval_sec before streaming GPS data
    set_gps_interval_sec()

    async def update_GPS_data(loop):
        global topic
        #global gps_interval_sec
        await asyncio.sleep(5)
        file = io.open('data.log', encoding='utf-8')
        print('Streaming GPS data to {} every {} secs...\n'.format(topic,gps_interval_sec))
        for line in file.readlines():
            if (line.startswith('$GPGGA')):
                #Stream gps data to the topic gps.stream every gps_interval_sec
                await asyncio.sleep(gps_interval_sec)
                try:
                    #Read data from data.log
                    msg = pynmea2.parse(line)

                    #Parse the GPS data in GPRMC format to extract required attributes
                    parse_data(msg)
                    print('GPS data being published is ',gps_data)
                    gps_message = {"message":json.dumps(gps_data)}
                    event_topic='event.'+topic+'.change'
                    await nc.publish(event_topic, json.dumps(gps_message).encode())

                except pynmea2.ParseError as e:
                    print('Parse error: {}'.format(e))
                    continue
            else:
                print('Incorrect GPS data format. Accepted format is GPGGA only')
                continue
    

    async def get_config_handler(msg):
        global topic
        global gps_interval_sec
        set_gps_interval_sec()                                                                     
        config={"gps_interval_sec":gps_interval_sec,"topic":topic}
        newmsg={"result":{"model": {"message":json.dumps(config) }}}
        await nc.publish(msg.reply, json.dumps(newmsg).encode())
    
    async def get_location_handler(msg):
        global current_gps_data
        current_gps_data=copy.deepcopy(gps_data)
        newmsg = {"result":{"model": {"message": json.dumps(current_gps_data)}}}
        await nc.publish(msg.reply, json.dumps(newmsg).encode())

    async def get_stream_handler(msg):
        newmsg = {"result":{"model": {"message": ""}}}
        await nc.publish(msg.reply, json.dumps(newmsg).encode())

    async def access_handler(msg):
        newmsg = {"result":{"get": True, "call": ""}}
        await nc.publish(msg.reply, json.dumps(newmsg).encode())

    await nc.subscribe("get.gps.location", cb=get_location_handler)
    await nc.subscribe("get.gps.config", cb=get_config_handler)
    await nc.subscribe("get.gps.stream", cb=get_stream_handler)
    await nc.subscribe("access.gps.location", cb=access_handler)
    await nc.subscribe("access.gps.config", cb=access_handler)
    await nc.subscribe("access.gps.stream", cb=access_handler)
    await update_GPS_data(loop)

if __name__ == '__main__':
    loop.create_task(run(loop))
    loop.run_forever()