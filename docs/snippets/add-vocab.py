from wordsiv import Vocab, WordSiv

# Create a Vocab from a file
de_vocab = Vocab(lang="de", data_file="de.tsv", bicameral=True)

# Add Vocab to WordSiv object
ws = WordSiv()
ws.add_vocab("de-subtitles", de_vocab)

# Try it out
print(ws.sent(vocab="de-subtitles"))
