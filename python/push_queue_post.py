from iron_mq import *

with open("twilio_payload.json", "r") as f:
    payload = f.read()

mq = IronMQ()

q = mq.queue("notifier")

q.post({"body": payload})
