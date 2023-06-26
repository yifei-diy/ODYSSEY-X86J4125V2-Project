import cv2
import time
import json
from paho.mqtt import client as mqtt_client
#########################MQTT消息服务定义##############################
broker = '192.168.8.251'
port = 1883
topic = "Topic/odyopencv"
client_id = 'opencv-ody'
username = 'opencv-ody'
password = 'public'

# JSON数据
data1 = {
    'Name': 'NiJie',
    'Authority':'Master'
}
# 将JSON数据转换为字符串
payload1 = json.dumps(data1)

# JSON数据
data2 = {
    'Name': 'Nano',
    'Authority':'Nano'
}
# 将JSON数据转换为字符串
payload2 = json.dumps(data2)

# JSON数据
data3= {
    'Name': 'MoMo',
    'Authority':'Guest'
}
# 将JSON数据转换为字符串
payload3 = json.dumps(data3)


#########################OpenCV##############################
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('face_trainer/trainer.yml')
faceCascade = cv2.CascadeClassifier(r"haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_SIMPLEX

idnum = 0
names = ['NiJie', 'MoMo']

cam = cv2.VideoCapture(0)
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

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

def opencv_Rec():
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=15,
        minSize=(int(minW), int(minH))
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        idnum, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        if confidence < 100:
            idnum = names[idnum]
            confidence = "{0}%".format(round(100 - confidence))
            if idnum=='NiJie':
                client.publish(topic, payload1)  # 发布消息
            elif idnum=='MoMo':
                client.publish(topic, payload3)  # 发布消息
        else:
            idnum = "unknown"
            confidence = "{0}%".format(round(100 - confidence))
            client.publish(topic, payload2)  # 发布消息

        cv2.putText(img, str(idnum), (x + 5, y - 5), font, 1, (0, 0, 255), 1)
        cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (0, 0, 0), 1)

    cv2.imshow('camera', img)
    k = cv2.waitKey(10)
    if k == 27:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    client = connect_mqtt()
    client.publish(topic, payload2)  # 发布消息
    while True:
        client.loop_start()
        opencv_Rec()