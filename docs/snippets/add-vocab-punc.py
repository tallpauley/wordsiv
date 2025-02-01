from wordsiv import Vocab, WordSiv

# Define the punctuation dictionary
de_punc = {
    "insert": {
        " ": 0.365,
        ", ": 0.403,
        ": ": 0.088,
        "; ": 0.058,
        "–": 0.057,
        "—": 0.022,
        " … ": 0.006,
    },
    "wrap_sent": {
        ("", "."): 0.923,
        ("", "!"): 0.034,
        ("", "?"): 0.04,
        ("", "…"): 0.003,
    },
    "wrap_inner": {
        ("", ""): 0.825,
        ("(", ")"): 0.133,
        ("‘", "’"): 0.013,
        ("“", "”"): 0.028,
    },
}

# Create a Vocab from a file, this time passing punctuation
de_vocab = Vocab(lang="de", data_file="de.tsv", bicameral=True, punctuation=de_punc)

# Add Vocab to WordSiv Object
ws = WordSiv()
ws.add_vocab("de-subtitles", de_vocab)

# Try it out, turning up punctuation randomness so we see more variation
print(ws.para(vocab="de-subtitles", rnd_punc=0.5))
