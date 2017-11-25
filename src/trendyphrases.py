from html.parser import HTMLParser
from urllib.request import urlopen
from random import choice, random
import re
import json
from enum import Enum

class WordType(Enum):
	NOUN = 1
	ADJECTIVE = 2
	VERB = 3
	OTHER = 4
	GENERIC = 5

with open("common_adj.txt") as f:
	all_adjectives = set(f.read().split())

with open("common_nouns.txt") as f:
	all_nouns = set(f.read().split())

with open("common_verbs.txt") as f:
	all_verbs = set(f.read().split())

all_generics = set(["music", "video", "trailer", "animation", "official", "teaser", "kid", "baby", "learn", "rhyme", "song"])

def word_type(word):
	if word in all_generics:
		return WordType.GENERIC
	
	for _ in range(10):
		if word in all_verbs and random() > 0.5:
			return WordType.VERB
		if word in all_adjectives and random() > 0.5:
			return WordType.ADJECTIVE
		if word in all_nouns and random() > 0.5:
			return WordType.NOUN
			
	return WordType.NOUN

phrases = []

class TrendingParser(HTMLParser):

	def __init__(self):
		super(TrendingParser, self).__init__()
		self.in_title = False
		self.current = ""
	
	def handle_starttag(self, tag, attrs):
		self.current = tag
		
		if tag == "a":
			for name, value in attrs:
				if name == "title" and self.in_title:
					phrases.append(value)
		elif tag == "h3":
			self.in_title = True
	
	def handle_endtag(self, tag):
		if tag == "h3":
			self.in_title = False

	def handle_data(self, data):
		pass

with urlopen("https://www.youtube.com/feed/trending?gl=US") as request:
	content = request.read().decode("utf-8")

parser = TrendingParser()
parser.feed(content)

excluded_words = set()
with open("exclude.txt", "r") as f:
	for line in f.readlines():
		excluded_words.add(line.strip())

regex = re.compile(r"[0-9]|[^\w\s]")
words = {}

for phrase in phrases:
	for word in regex.sub("", phrase).split():
		word = word.lower()
		
		if word in excluded_words or len(word) <= 3:
			continue
			
		if word[-1] == "s" and word[-2] != "s":
			word = word[0:len(word)-1]

		if word in words:
			words[word] = words[word] + 1
		else:
			words[word] = 1

weighted_words = []
for word in words:
	for _ in range(words[word]**2):
		weighted_words.append(word)

def random_by_type(target_type):
	w = choice(weighted_words)
	
	tries = 0
	while word_type(w) != target_type:
		w = choice(weighted_words)
		tries+=1
		if tries > 1000:
			return None
	
	for i in range(0, weighted_words.count(w)):
		weighted_words.remove(w)
	return w

characters = []
while len(characters) < 10:
	noun = random_by_type(WordType.NOUN)
	adj = random_by_type(WordType.ADJECTIVE)
	
	if noun == None or adj == None:
		break
		
	char = {}
	char["name"] = noun
	char["adj"] = adj
	characters.append(char)

items = []
while len(items) < 30:
	item = random_by_type(WordType.NOUN)
	if item == None:
		break
	items.append(item)

actions = []
while len(actions) < 20:
	verb = random_by_type(WordType.VERB)
	if verb == None:
		break
	actions.append(verb)

generics = []
for i in range(0, 10):
	gen = random_by_type(WordType.GENERIC)
	if gen == None:
		break
	generics.append(gen)

result = {}
result["characters"] = characters
result["items"] = items
result["actions"] = actions

char1 = characters[0]
char2 = characters[1]
item1 = items[0]
item2 = items[1]
action1 = actions[0]
action2 = actions[1]

name = char1["adj"] + " " + char1["name"] + " and " + char2["adj"] + " " + char2["name"] + " "
if(random() < 0.25): name = name + item1 + " "
if(random() < 0.25): name = name + item2 + " "
if(random() < 0.25): name = name + action1 + " "
if(random() < 0.25): name = name + action1 + " "

if(random() < 0.5):
	name = name + "adventure "
else:
	name = name + "journey "

for gen in generics:
	name = name + gen + " "

name = name.upper().strip()
result["name"] = name

print(json.dumps(result))
