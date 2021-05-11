from nltk.corpus import brown, reuters, gutenberg
from collections import Counter
import string
import json


corpa = "\n".join((brown.raw(), gutenberg.raw(), reuters.raw()))

trigrams = []

for a, b, c in zip(*[iter(corpa)] * 3):
    all_letters = string.ascii_lowercase + string.ascii_uppercase
    if all(char in all_letters for char in (a, b, c)):
        trigrams.append("".join((a, b, c)))

trigrams = list(Counter(trigrams).most_common())

with open("trigrams.json", "w") as f:
    json.dump(trigrams, f)
