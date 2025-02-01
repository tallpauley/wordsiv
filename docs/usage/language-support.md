# Language Support

## Vocab
In WordSiv, a [Vocab](../api-reference.md#wordsiv.Vocab) is an object that contains
a word list and other language-specific data that allow a WordSiv object to
appropriately filter words and generate text.

!!! Note
    I considered naming this object **WordList**, but it also can contain
    word counts and punctuation data. I considered calling it **Lang**, but it's
    possible to have more than one set of words (and punctuation, etc.) per
    language. I can imagine having Vocabs derived from different genres of text:
    `en-news`, `en-wiki`, etc!

### Using a Built-in Vocab

See [Basic Usage](basic-usage.md) for how to list and select a built-in Vocab.
If you're curious about the origin/license[^1] of these lists you can examine
the built-in Vocabs in [wordsiv/_vocab_data][vocab-data].

### Creating a custom Vocab

It's easy to add your own Vocab to WordSiv. The harder part is actually deriving
wordlists from a [text corpus](https://en.wikipedia.org/wiki/Text_corpus)) and
refining the capitalization (if applicable), which we won't detail here.

Let's say we grab the top 20 German words from this [frequency wordlist derived
from OpenSubtitles][hermit-de], and save it as `de-words.tsv` (replacing spaces
with tabs):
```
--8<-- "de.tsv"
```

We can now create a Vocab and add it to WordSiv:
```python
--8<-- "add-vocab.py"
```

We get the output:
> Die du die der ich nicht sie das und e

#### Adding Custom Punctuation to a Vocab

But what if we want punctuation? We have some default punctuation for the
built-in languages in [wordsiv/_punctuation.py][punctuation-py], but not yet for
German (at the time of writing). Let's copy/paste the English one (for now[^2])
and try it out:
```python
--8<-- "add-vocab-punc.py"
```

Now we see punctuation:
> Ich ist mit das ich (du und) mit es sie… Nicht das was zu sie—du die ja nicht
> und zu ist du? Das er das “wir” ich was sie der du mit das die und zu ich. In
> und in, ich ja ich die der das (nicht er sie ich) mir.


### Contributing Vocabs to WordSiv

WordSiv is as only as good as the Vocabs (and punctuation dictionaries!) that
are available to it, and we'd love any help on improving language support. Feel
free to [create an issue on the GitHub
repo](https://github.com/tallpauley/wordsiv/issues) if you're interested in
helping us improve language support. You don't even have to be a programmer—we
just need native speakers to help us construct useful Vocabs. However, if you
are looking to learn some programming, building wordlists and punctuation can be
a fun first project (and I'd be glad to help!).

My long-term vision is to build a community-maintained project (outside of
WordSiv) that has a huge selection of multilingual proofing text, wordlists,
punctuation, etc. and resources and code that enable the global type community
to more easily leverage the language data that is commonplace in
NLP/linguistics/engineering circles. A lot of the source data
[already](https://github.com/simoncozens/gobbet)
[exists](https://cldr.unicode.org/), it just needs to be adapted for the
needs/tooling of type designers.

[^1]: Licensing for wordlists is a bit odd, because they're often built by
crawling a bunch of data with all kinds of licenses. I'm just doing my best here
to respect licenses where I can!
[^2]: I'd recommend deriving punctuation frequencies for the target language
from [real text][leipzig], and normalizing the probabilities between 0 and 1. I
have a script that builds these dictionaries, which I hope to publish soon!

[leipzig]: https://wortschatz.uni-leipzig.de/en/
[vocab-data]:
    https://github.com/tallpauley/wordsiv/tree/main/wordsiv/_vocab_data
[punctuation-py]:
    https://github.com/tallpauley/wordsiv/tree/main/wordsiv/_punctuation.py
[hermit-de]:
    https://github.com/hermitdave/FrequencyWords/blob/master/content/2016/de/de_50k.txt
