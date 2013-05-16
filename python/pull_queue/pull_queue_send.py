import sendgrid
from iron_helper import WorkerArgs
from iron_mq import IronMQ
import json

args = WorkerArgs()
username = args.config["username"]
password = args.config["password"]
queue_name = args.config["queue"]
s = sendgrid.Sendgrid(username, password, secure=True)
mq = IronMQ()
queue = mq.queue(queue_name)

def getMessage():
    resp = queue.get()
    if "messages" not in resp:
        return None
    if len(resp["messages"]) < 1:
        return None
    return resp["messages"][0]

msg = getMessage()
print msg
while msg is not None:
    msg["body"] = json.loads(msg["body"])
    from_address = None
    from_name = None
    if isinstance(msg["body"]["from"], basestring):
        from_address = msg["body"]["from"]
    else:
        from_address = msg["body"]["from"]["address"]
        if "name" in msg["body"]["from"]:
            from_name = msg["body"]["from"]["name"]
    reply_to = None
    if "reply_to" in msg["body"]:
        reply_to = msg["body"]["reply_to"]
    subject = msg["body"]["subject"]

    text_body = None
    html_body = None
    if isinstance(msg["body"]["body"], basestring):
        text_body = msg["body"]["body"]
    else:
        if "text" in msg["body"]["body"]:
            text_body = msg["body"]["body"]["text"]
        if "html" in msg["body"]["body"]:
            html_body = msg["body"]["body"]["html"]

    recipients = []
    if "to" in msg["body"]:
        if isinstance(msg["body"]["to"], basestring):
            recipients = [msg["body"]["to"]]
        else:
            recipients = msg["body"]["to"]

    from_param = from_address
    if from_name is not None:
        from_param = (from_address, from_name)

    message = sendgrid.Message(from_param, subject, text_body, html_body)
    for recipient in recipients:
        message.add_to(recipient["address"], recipient["name"])

    if reply_to is not None:
        message.set_replyto(reply_to)

    s.web.send(message)
    
    print "Sent message #%s" % (msg["id"],)

    queue.delete(msg["id"])

    msg = getMessage()

print "Ran out of messages to process."
