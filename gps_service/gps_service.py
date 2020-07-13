import asyncio
import os
import json
import pynmea2
import io
import copy
import serial
import time
import logging
from nats.aio.client import Client as NATS
from configparser import SafeConfigParser
from logging.handlers import RotatingFileHandler

loop = asyncio.get_event_loop()
count = 0
subscriptions = dict()
gps_data={}
current_gps_data={}
gps_interval_sec=5
mode='production'
topic='gps.stream'

#Get hold of the configuration file (package_config.ini)
moduledir = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.getenv("CAF_APP_PATH", moduledir)
tcfg = os.path.join(BASEDIR,  "package_config.ini")
CONFIG_FILE = os.getenv("CAF_APP_CONFIG_FILE", tcfg)
cfg = SafeConfigParser()
cfg.read(CONFIG_FILE)

logger = logging.getLogger("IOxvApp")

def setup_logging(cfg):
    log_file_dir = os.getenv("CAF_APP_LOG_DIR", "/tmp")
    log_file_path = os.path.join(log_file_dir, "ioxv_app.log")
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    loglevel = cfg.getint("logging", "log_level")
    logger.setLevel(loglevel)
    
    rfh = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=3)
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)

def generate_error_response():                                                                        
    global gps_data                                                                                   
    status_code='404'                                                                                 
    error_message='GPS data not available. Check the IOS configuration'                               
    gps_data['return-code']=status_code                                                               
    gps_data['description']=error_message

def get_config():
    global cfg
    global gps_interval_sec
    global mode
    for section in ["gps-config"]:
        if cfg.has_section(section):
            if cfg.has_option(section, "service-mode"):
                mode=cfg.get(section, "service-mode")
            if cfg.has_option(section,"interval"):
                #Read interval from package_config.ini only if the section interval exists in the file
                gps_interval_sec=cfg.getint("gps-config","interval")

def format_timestamp(timeval,dateval):
    formatted_time = str(dateval.strftime("%a %b %d "))+str(timeval)+str(dateval.strftime(" %Y"))
    return formatted_time

def parse_data(msg):
    global gps_data
    status_code='200'

    latitude=msg.lat
    longitude=msg.lon
    altitude=msg.altitude
    timestamp=msg.timestamp

    gps_data['return-code']=status_code                                                               
    gps_data['latitude']=0                                                                            
    gps_data['longitude']=0                                                                           
    gps_data['altitude']=0                                                                                                                                          
    gps_data['timestamp']=str(time.time())                                                            
                                                                                                      
    if latitude!= '' and latitude != None:                                                            
        gps_data['latitude']=latitude                                                                 
    if longitude != '' and longitude != None:                                                         
        gps_data['longitude']=longitude                                                               
    if altitude != '' and altitude != None:                                                           
       gps_data['altitude']=altitude                                                                  
    if timestamp != '' and timestamp !=None:                                                          
       gps_data['timestamp']=str(timestamp)

async def run(loop):
    #global gps_interval_sec
    nc = NATS()
    url=os.environ.get("message_broker_IP_ADDRESS")+":"+os.environ.get("message_broker_TCP_4222_PORT")
    await nc.connect(url,loop=loop)

    #Get the parameters gps_interval_sec and mode before streaming GPS data
    get_config()

    async def update_GPS_data(loop):
        global topic
        #global gps_interval_sec
        await asyncio.sleep(5)
        if mode == "demo":
            file = io.open('data.log', encoding='utf-8')
            print('Streaming GPS data to {} every {} secs...\n'.format(topic,gps_interval_sec))
            for line in file.readlines():
                if (line.startswith('$GPGGA')):
                    #Stream gps data to the topic gps.stream every gps_interval_sec
                    await asyncio.sleep(gps_interval_sec)
                    try:
                        #Read data from data.log
                        msg = pynmea2.parse(line)

                        print(repr(msg))

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

        elif mode == "production":
            print('Production mode: Service under construction')
            #The environment variable name is set as HOST_GPS under devices in package.yaml file
            serial_dev=os.getenv("HOST_GPS")
            if serial_dev is None:
                print ('No serial path specified in HOST_MOTION')
                serial_dev="/dev/tty3"
                # loop.stop()
            sdev = serial.Serial(port=serial_dev, baudrate=9600)
            sdev.bytesize = serial.EIGHTBITS #number of bits per bytes

            sdev.parity = serial.PARITY_NONE #set parity check: no parity

            sdev.stopbits = serial.STOPBITS_ONE

            sdev.timeout = 5
            # while(1):
            if sdev.inWaiting()==0:                                                                   
               event_topic='event.'+topic+'.change'                                                   
               generate_error_response()                                                              
               gps_message = {"message":json.dumps(gps_data)}                                         
               print('Error message being published',gps_message)                                     
               await nc.publish(event_topic, json.dumps(gps_message).encode())                                                                              
               while sdev.inWaiting() > 0:                                                           
                    try:                                                                              
                        sensval = sdev.readline()                                                     
                        print("Sensor value= %s", sensval)                                            
                    except serial.SerialException as e:                                               
                        print('Device error: {}'.format(e))                                           
                        break

    async def get_config_handler(msg):
        global topic
        global gps_interval_sec
        get_config()                                                                     
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
    setup_logging(cfg)
    loop.create_task(run(loop))
    loop.run_forever()