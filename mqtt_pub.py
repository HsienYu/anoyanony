import paho.mqtt.client as paho
import argparse

if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description="MQTT Client")
    argparse.add_argument('--topic', type=str, required=True)
    argparse.add_argument('--msg', type=str, required=True)
    args = argparse.parse_args()

    print(args.msg)
    broker = "127.0.0.1"
    port = 1883

    def on_publish(client, userdata, result):  # create function for callback
        print("data published \n")
        pass

    client1 = paho.Client("control1")  # create client object
    client1.on_publish = on_publish  # assign function to callback
    client1.connect(broker, port)  # establish connection
    ret = client1.publish(args.topic, args.msg)  # publish
