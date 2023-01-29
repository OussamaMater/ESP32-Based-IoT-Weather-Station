import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient
from machine import I2C, Pin
from lib.i2c_lcd import I2cLcd


# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_TOPIC = "esp32-weather-station-2023"
MQTT_USER = ""
MQTT_PASSWORD = ""

print("Connecting to WiFi", end="")

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')

while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)

print(" Connected!")

print("Connecting to MQTT server... ", end="")

client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    user=MQTT_USER,
    password=MQTT_PASSWORD
)

client.connect()

print("Connected!")

AddressOfLcd = 0x27
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, AddressOfLcd, 2, 16)


def displayToLCD(upperText, lowerText):
    lcd.move_to(0, 0)
    lcd.putstr("Temp in C = " + str(upperText))
    lcd.move_to(0, 1)
    lcd.putstr("Humidity = " + str(lowerText))


# DHT
sensor = dht.DHT22(Pin(15))

prev_weather = ""
while True:
    sensor.measure()

    displayToLCD(sensor.temperature(), sensor.humidity())

    payload = ujson.dumps({
        "temp": sensor.temperature(),
        "humidity": sensor.humidity(),
    })

    if payload != prev_weather:
        client.publish(MQTT_TOPIC, payload)
        prev_weather = payload
    else:
        print("No change, won't publish")

    time.sleep(1)
