# Complete project details at https://RandomNerdTutorials.com
from umqttsimple import MQTTClient
import time
import ubinascii
import machine
import dht

temp_sensor = dht.DHT11(machine.Pin(14))

led = machine.Pin(4, machine.Pin.OUT)

topic_sub = b'CASA/controle1'
topic_pub = b'CASA/temperatura1'
topic_pub_status = b'CASA/status' 

last_message = 0
message_interval = 20
counter = 0

client_id = ubinascii.hexlify(machine.unique_id())

mqtt_server = conf["mqtt_server"]
server_port = conf["server_port"] 
mqtt_user = conf["mqtt_user"]
mqtt_password = conf["mqtt_password"]


def sub_cb(topic, msg):
  global topic_sub
  print((topic, msg))
  print(topic_sub)
  if topic == topic_sub and msg == b'l':
    print('Ligar LED')
    led.on()
  if topic == topic_sub and msg == b'd':
    print('Desligar LED')
    led.off() 

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub, server_port, mqtt_user, mqtt_password
  client = MQTTClient(client_id, mqtt_server, server_port, mqtt_user, mqtt_password)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      temp_sensor.measure()
      temp = temp_sensor.temperature()

      msg = b'MSG %d %3.1f ' % (counter,temp) 
      msg_temp = b'%3.1f' % (temp)
      client.publish(topic_pub, msg_temp)
      client.publish(topic_pub_status, msg)
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()




