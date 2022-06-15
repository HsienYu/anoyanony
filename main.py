import asyncio
import json
from contextlib import AsyncExitStack, asynccontextmanager
from asyncio_mqtt import Client, MqttError
from pytwinkle import Twinkle
import subprocess
import time


async def advanced():
    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        # Connect to the MQTT broker
        client = Client("127.0.0.1")
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "sip/a/#",
        )
        for topic_filter in topic_filters:
            # Log all messages that matches the filter
            manager = client.filtered_messages(topic_filter)
            messages = await stack.enter_async_context(manager)
            template = f'[topic_filter="{topic_filter}"] {{}}'
            task = asyncio.create_task(log_messages(messages, template))
            tasks.add(task)

        # Messages that doesn't match a filter will get logged here
        messages = await stack.enter_async_context(client.unfiltered_messages())
        task = asyncio.create_task(log_messages(messages, "[unfiltered] {}"))
        tasks.add(task)

        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("sip/a/#")

        # start sip service

        task = asyncio.create_task(mTP.run())

        tasks.add(task)

        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)


async def log_messages(messages, template):

    async for message in messages:
        # UTF8-encoded string (hence the `bytes.decode` call).
        # logMSG = template.format(message.payload.decode())
        # print(logMSG)
        decoded_message = str(message.payload.decode("utf-8"))
        res = json.loads(decoded_message)
        msg = res.get("msg")
        number = res.get("number")
        print(f"msg: {msg} number: {number}")
        if msg == 'call':
            print("call the number " + number)
            mTP.call(number)
        elif msg == 'bye':
            print("bye the call")
            mTP.bye()
        elif msg == 'test':
            print("test")


async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        try:
            task.cancel()
            await task
        except asyncio.CancelledError:
            pass


async def main():
    # Run the advanced_example indefinitely. Reconnect automatically
    # if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await advanced()
        except MqttError as error:
            print(
                f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


def callback(event, *args):
    if event == "registration_succeeded":
        uri, expires = args
        print("registration succeeded, uri: %s, expires in %s seconds" %
              (uri, expires))
        # The module keeps the session, you havent to register
    if event == "new_msg":
        msg = args[0]
        print("new_msg!: "+str(msg))

    if event == "incoming_call":
        call = args[0]
        print("call: "+str(call))

    if event == "cancelled_call":
        line = args[0]
        print("call cancelled, line: %s" % (line))

    if event == "answered_call":
        call = args[0]
        print("answered: %s" % (str(call)))
        message = json.dumps({"msg": "answercall", "number": "1"})
        topic = "sip/a"
        mqtt_pub(topic, message)

    if event == "ended_call":
        line = args[0]
        print("call ended, line: %s" % (line))
        message = json.dumps({"msg": "endcall", "number": "1"})
        topic = "sip/a"
        mqtt_pub(topic, message)


def mqtt_pub(topic, message):
    p = subprocess.Popen(['python', 'mqtt_pub.py', '--topic',
                          topic, '--msg', message])
    time.sleep(1)
    p.kill()


if __name__ == "__main__":
    mTP = Twinkle(callback)
    asyncio.run(main())
