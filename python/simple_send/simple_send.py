import sendgrid
from iron_helper import WorkerArgs

args = WorkerArgs()
username = args.config["username"]
password = args.config["password"]
s = sendgrid.Sendgrid(username, password, secure=True)

from_address = None
from_name = None
if isinstance(args.payload["from"], basestring):
    from_address = args.payload["from"]
else:
    from_address = args.payload["from"]["address"]
    if "name" in args.payload["from"]:
        from_name = args.payload["from"]["name"]
reply_to = None
if "reply_to" in args.payload:
    reply_to = args.payload["reply_to"]
subject = args.payload["subject"]

text_body = None
html_body = None
if isinstance(args.payload["body"], basestring):
    text_body = args.payload["body"]
else:
    if "text" in args.payload["body"]:
        text_body = args.payload["body"]["text"]
    if "html" in args.payload["body"]:
        html_body = args.payload["body"]["html"]

recipients = []
if "to" in args.payload:
    if isinstance(args.payload["to"], basestring):
        recipients = [args.payload["to"]]
    else:
        recipients = args.payload["to"]

from_param = from_address
if from_name is not None:
    from_param = (from_address, from_name)

message = sendgrid.Message(from_param, subject, text_body, html_body)
for recipient in recipients:
    message.add_to(recipient["address"], recipient["name"])

if reply_to is not None:
    message.set_replyto(reply_to)

s.web.send(message)
