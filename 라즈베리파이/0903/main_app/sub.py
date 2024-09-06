import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags ,rc):
    if rc==0:
        print("connected OK")
    else:
        print("bad connection")

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("sub = " +str(mid)+" "+ str(granted_qos))

def on_message(client, userdata, msg):
    print("HI"+str(msg.payload.decode("utf-8")))

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message

client.connect('localhost',1883)
client.subscribe('controller',1)
client.loop_forever()
