####################
# Loosely-adapted version of https://github.com/thomasboyt/python-markov/blob/master/examples/AChristmasMarkov/markov.py
####################

import json, random

# source should be a list of lines to put in
# if importing a larger source without separate lines, simply make it a one-element list

class MarkovChain:
    def __init__(self):
        self.table = {}

    def create_table(self, source):
        words = source.split(" ")
        for index, word in enumerate(words):
            if index+1 < len(words):
                if word not in self.table:
                    self.table[word] = {}
                if words[index+1] not in self.table[word]:
                    self.table[word][words[index+1]] = 1
                else:
                    self.table[word][words[index+1]] += 1

    def save_table(self, file):
        serialized = json.JSONEncoder().encode(self.table)
        f = open(file, 'w')
        f.write(serialized)
        f.close()

    def parse_table(self, serialized_table):
        table = json.JSONDecoder().decode(serialized_table)
        self.table = table

    def generate_chain(self, length, words=None):
        table = self.table
        if words is None:
            words = []
            # pick a random word to start the chain
            words.append(random.choice(table.keys()))

        replaced_chars = {
                "\n": " ",
                "\r": "",
                ";": "",
                ".": "",
                ",": "",
                "!": "",
                "?": "",
                '"': ""
        }
        new_words = " ".join(words)
        for c in replaced_chars:
            new_words = new_words.replace(c, replaced_chars[c])

        new_words = new_words.split(" ")

        while len(words) < length:
            last_idx = len(new_words)-1
            last_word = new_words[last_idx]

            try:
                entries = table[last_word]
            except KeyError:
                return " ".join(words)

            probabilities = {}

            total_count = sum(entries.values())
            choice = random.randint(0, total_count-1)
            word = weighted_probability(entries, choice)
            words.append(word)

        return " ".join(words)


def weighted_probability(entries, rnd):
    for word, weight in entries.iteritems():
        if (rnd < weight):
            return word
        rnd -= weight
