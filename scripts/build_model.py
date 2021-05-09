from markovify import Text
from nltk.corpus import gutenberg, brown, inaugural, reuters
from wordsiv import SivText

text = '\n'.join((gutenberg.raw(fileid) for fileid in gutenberg.fileids() if 'bible' not in fileid))

text_model = SivText(text, retain_original=False, state_size=1)

model_json = text_model.to_json()

with open('gutenberg.json', 'w') as f:
    f.write(model_json)