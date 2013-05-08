##########
# BASED ON https://github.com/thomasboyt/python-markov/blob/master/examples/AChristmasMarkov/christmas_markov.py
##########

import os, json
from markov import MarkovChain

def sanitize(text):
    replaced_chars = {
            "\n": " ",
            "\r": "",
            ";": "",
            ".": "",
            "!": "",
            ",": "",
            "?": "",
            '"': ""
    }
    for c in replaced_chars:
        text = text.replace(c, replaced_chars[c])
    return text

chain = MarkovChain()
f = open("markov_source.txt")
source = sanitize(f.read())
f.close()
chain.create_table(source)
chain.save_table("markov_source.json")
