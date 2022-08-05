import asyncio
import json
from contextlib import AsyncExitStack, asynccontextmanager
from asyncio_mqtt import Client, MqttError
from pytwinkle import Twinkle
import subprocess
import time
import os
import signal

pid = 0


async def advanced():
    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        # Connect to the MQTT broker
        client = Client("192.168.100.2")
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "status",
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
        await client.subscribe("status")

        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)


async def log_messages(messages, template):

    async for message in messages:
        # UTF8-encoded string (hence the `bytes.decode` call).
        # logMSG = template.format(message.payload.decode())
        # print(logMSG)
        decoded_message = str(message.payload.decode("utf-8"))
        # print(decoded_message)
        if decoded_message == 'sip_start':
            print("sip service start")
            pro = subprocess.Popen('python main.py', stdout=subprocess.PIPE,
                                   shell=True, preexec_fn=os.setsid)
            pid = pro.pid
        elif decoded_message == 'sip_stop':
            print("sip service stop")
            os.killpg(os.getpgid(pid), signal.SIGTERM)


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


if __name__ == "__main__":
    asyncio.run(main())
