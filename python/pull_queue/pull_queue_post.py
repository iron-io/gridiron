from iron_mq import *
import json

with open("pull_queue_payload.json", "r") as f:
    payload = f.read()

with open("pull_queue_config.json", "r") as f:
    config = json.loads(f.read())

mq = IronMQ()

q = mq.queue(config["queue"])

q.post({"body": payload})
