# python 3.6

import random
import time
import json
from paho.mqtt import client as mqtt_client

broker = '124.71.224.174'
port = 1883
topic = "Topic/odyssey"
client_id = 'ODYSSEY'
username = 'ODYSSEY'
password = 'public'

# JSON数据
data = {
    'name': 'John Doe',
    'age': 30,
    'city': 'New York'
}

# 将JSON数据转换为字符串
payload = json.dumps(data)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username=username, password=password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)
        client.publish(topic, payload)  # 发布消息


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()