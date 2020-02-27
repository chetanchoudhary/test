def simulationThingworx(connection, frequency, timeInterval, payload):
    import sys
    import paho.mqtt.client as mqtt
    import time
    import json
    import random
    from libs.num import randomGen

    # Callback from MQTT call
    def on_message(client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    ##############################################################################################################################
    # Configurations
    broker = connection["broker"]
    topic = connection["topic"]
    client = mqtt.Client("simulator")

    payloadLength = len(payload["list"])

    class PayloadModel:
        def __init__(self, fieldName, minRange, maxRange):
            self.fieldName = fieldName
            self.minRange = minRange
            self.maxRange = maxRange

    payloadList = []
    for i in payload["list"]:
        payloadList.append(PayloadModel(i["fieldName"], i["minRange"], i["maxRange"]))

    finalPayload = {}

    def payloadGen(count):

        for i in range(payloadLength):
            freq = frequency
            numArray = []
            for j in range(freq):
                a = random.randint(payloadList[i].minRange, payloadList[i].maxRange)
                numArray.append(a)
            numArray = sorted(numArray)

            fieldName = str(payloadList[i].fieldName)
            value = str(numArray[count])
            finalPayload.update({fieldName: value})
        return finalPayload

    # payload

    ##############################################################################################################################
    # Publishing Data to Cloud

    def valueChange(test):
        client.on_message = on_message
        print("Connecting to Broker : ", broker)
        client.connect(broker)
        client.loop_start()
        client.publish(topic, test)
        print("published to " + topic)
        print(test)
        time.sleep(4)
        client.loop_stop()

    ##############################################################################################################################

    # Getting Temperature and Humidity from DHT11 sensor.

    def valueGen(minRange, maxRange):
        a = random.randint(minRange, maxRange)
        return a

    # Sending data to Thingworx Cloud Continously using MQTT
    i = 0
    count = 0
    while i < frequency:
        test = payloadGen(count)
        count = count + 1
        testJson = json.dumps(test)
        valueChange(testJson)
        i = i + 1
        time.sleep(timeInterval)
