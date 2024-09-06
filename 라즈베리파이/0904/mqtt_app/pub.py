import paho.mqtt.client as mqtt
import json, time

def on_connect(client, userdata, flags ,rc):
    if rc==0:
        print("connected OK")
    else:
        print("bad connection")

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid=",mid)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish


value = 0
while True:
    client.connect('localhost',1883)
    client.publish('common',json.dumps({"test":value}),1)
    # client.loop_forever()
    client.disconnect()
    value +=1
    value %=200
    # time.sleep(0.0)
# 
# client.loop_stop()