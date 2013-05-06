from twilio.rest import TwilioRestClient
from iron_helper import WorkerArgs

args = WorkerArgs()
account = args.config["account"]
token = args.config["token"]

client = TwilioRestClient(account, token)

from_number = args.payload["from_num"]
to_number = args.payload["to_num"]

if isinstance(args.payload["body"], basestring):
    body = args.payload["body"][:140]
else:
    if "text" in args.payload["body"]:
        body = args.payload["body"]["text"][:140]
    else:
        body = args.payload["body"]["html"][:140]

client.sms.messages.create(to=to_number, from_=from_number, body=body)
