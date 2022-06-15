import subprocess
import time
import json


def mqtt_pub(topic, msg):
    p = subprocess.Popen(['python', 'mqtt_pub.py', '--topic',
                          topic, '--msg', msg])
    time.sleep(1)
    p.kill()


message = json.dumps({"msg": "call", "number": "0935932247"})
mqtt_pub("sip/a", message)
