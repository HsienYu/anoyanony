# import subprocess
# import time
# import json


# def mqtt_pub(topic, msg):
#     p = subprocess.Popen(['python', 'mqtt_pub.py', '--topic',
#                           topic, '--msg', msg])
#     time.sleep(1)
#     p.kill()


# message = json.dumps({"msg": "call", "number": "0935932247"})
# mqtt_pub("sip/a", message)


#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

from threading import Thread
try:
    from queue import Queue  # Python 3 import
except ImportError:
    from Queue import Queue  # Python 2 import

import speech_recognition as sr


r = sr.Recognizer()
audio_queue = Queue()


def recognize_worker():
    # this runs in a background thread
    while True:
        audio = audio_queue.get()  # retrieve the next audio processing job from the main thread
        if audio is None:
            break  # stop processing if the main thread is done

        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            print(r.recognize_google(audio, language='zh-TW'))
        except sr.UnknownValueError:
            print("could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(e))

        audio_queue.task_done()  # mark the audio processing job as completed in the queue


# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()
print(sr.Microphone().list_microphone_names())
with sr.Microphone(3) as source:
    try:
        while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop
