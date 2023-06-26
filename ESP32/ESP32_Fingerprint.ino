#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

int BUTTON_Pin=1;
int BUTTON_level; 
int Relay1_Pin=2;   
int AccessControl;
int finger_level;

// WiFi
const char *ssid = "GLAXT1800"; // Enter your WiFi name
const char *password = "Lsx@ubuntu";  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "192.168.8.5";
const char *topic =  "Topic/odyFingerprintSub";   //消息接受，温度设定值输入

const char *topic1 = "Topic/odyFingerPub";    //消息发布主题
const char *mqtt_username = "ESP32C3-test02";
const char *mqtt_password = "public";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

void setup()
{
  // Set software serial baud to 115200;
  Serial.begin(115200); 
  pinMode(Relay1_Pin, OUTPUT);  
  pinMode(BUTTON_Pin, INPUT); // 将引脚设置为输入模式
   
  // connecting to a WiFi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to the WiFi network");
  //connecting to a mqtt broker
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) 
  {
    String client_id = "esp32-client-";
    client_id += String(WiFi.macAddress());
    Serial.printf("The client %s connects to the public mqtt broker\n", client_id.c_str());
    if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) 
    {
      Serial.println("Public emqx mqtt broker connected");
    } 
    else 
    {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
  // publish and subscribe
  //client.publish(topic1, "Hi EMQX I'm ESP32 ^^");
  client.subscribe(topic);
}

// Define the callback function
void callback(char* topic, byte* payload, unsigned int length)
{

    //Serial.println(topic);
    //Serial.println((char *)payload);

    //接下来是收到的json字符串的解析
    DynamicJsonDocument doc(100);
    DeserializationError error = deserializeJson(doc, payload);
    if (error)
    {
      Serial.println("parse json failed");
      return;
    }
    JsonObject setAlinkMsgObj = doc.as<JsonObject>();
    serializeJsonPretty(setAlinkMsgObj, Serial);
    Serial.println();

    //这里是一个点灯小逻辑
    AccessControl = setAlinkMsgObj["AccessControl"]; 
 
    //Serial.println(SETLUM);
}

void loop() 
{
  delay(200);
  BUTTON_level=digitalRead(BUTTON_Pin); // 读取引脚电平
   if (BUTTON_level == HIGH) 
   {
      finger_level=1;
      digitalWrite(Relay1_Pin, HIGH);   // 打开继电器
      delay(3000);
   } 
   else
   {
     digitalWrite(Relay1_Pin, LOW);   // 关闭继电器
     finger_level=0;
   }
  
  if(AccessControl==1)
  {
    digitalWrite(Relay1_Pin, HIGH);   // 打开继电器
    //Serial.printf("FanStart:ON\n");
  }
  else if(AccessControl==0)
  {
    digitalWrite(Relay1_Pin, LOW);   // 关闭继电器
    //Serial.printf("FanStart:OFF\n");
  }

  
  
  // 生成要发送的 JSON 数据
  StaticJsonDocument<200> jsonDoc;
  jsonDoc["Fingerprint"] = finger_level;
  
  String jsonData;
  serializeJson(jsonDoc, jsonData);
  client.publish(topic1,jsonData.c_str());
  client.loop();
}
