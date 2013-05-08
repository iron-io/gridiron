import sendgrid
from iron_helper import WorkerArgs
from markov import MarkovChain

args = WorkerArgs(multipart=True)
username = args.config["username"]
password = args.config["password"]
s = sendgrid.Sendgrid(username, password, secure=True)

from_address = None
from_name = None
if isinstance(args.config["from"], basestring):
    from_address = args.config["from"]
else:
    from_address = args.config["from"]["address"]
    if "name" in args.config["from"]:
        from_name = args.config["from"]["name"]
reply_to = None
if "reply_to" in args.config:
    reply_to = args.config["reply_to"]


subject = args.payload["subject"][0]
text_body = args.payload["text"][0]
sender = args.payload["from"][0]

print "Sender: %s" % (sender,)
print "Got text: %s" % (text_body,)

chain = MarkovChain()
f = open("markov_source.json")
raw_table = f.read()
f.close()

chain.parse_table(raw_table)
text_words = [word.strip() for word in text_body.split(" ")]
text_body = chain.generate_chain(length=len(text_words) + 1, words=text_words)

print "New text: %s" % (text_body,)

from_param = from_address
if from_name is not None:
    from_param = (from_address, from_name)

message = sendgrid.Message(from_param, subject, text_body)

sender_name = None
sender_email = sender
if sender.find("<") >= 0:
    sender_name = sender[:sender.find("<")-1]
    sender_email = sender[sender.find("<")+1:sender.find(">")]
message.add_to(sender_email, sender_name)

if reply_to is not None:
    message.set_replyto(reply_to)

s.web.send(message)
