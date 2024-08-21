
# Wordsiv

Wordsiv is a Python library for generating [lipograms](https://en.wikipedia.org/wiki/Lipogram) for [type proofing](https://ohnotype.co/blog/proof-it).


## Installation in DrawBot

1. Install the `wordsiv` package via **Python->Install Python Packages**:
     - Enter ```git+https://github.com/tallpauley/wordsiv``` and click **Go!**
     - ***Note:*** you'll probably see lots of red text but it
       should still work just fine

    ![Screenshot of DrawBot "Install Python
    Packages" Window](docs/images/drawbot-install.jpg)

2. Install the desired Source packages in the same window:

    ```git+http://github.com/tallpauley/wordsiv-sources```

3. You can now 


## Installation

First, install wordsiv with pip:

```bash
$ pip install git+https://github.com/tallpauley/wordsiv # byexample: +pass
```

Then install some **sources**:

```bash
pip install git+https://github.com/tallpauley/wordsiv-sources
```

Now you can make meaningless lipograms in Python:

```python
>>> import wordsiv as wsv
>>> wsv.sent(model='en_trillion', glyphs='HAMBUGERFONTSIVhambugerfontsiv.,')
('I might go over the instant to the streets in the air of those the same be '
 'haunting')
```

## Sources

Wordsiv first needs some words, which come in the form of
[Sources](https://github.com/tallpauley/wordsiv/blob/main/wordsiv/source.py):
objects which supply the raw word data.

These Sources are available via [Source
Packages](https://github.com/tallpauley/wordsiv-source-packages), which are
simply Python Packages. Let's install some:

```bash
base=https://github.com/tallpauley/wordsiv-source-packages/releases/download

# A markov model trained on public domain books
$ pkg=en_markov_gutenberg-0.1.0/en_markov_gutenberg-0.1.0-py3-none-any.whl
$ pip install $base/$pkg   # byexample: +pass

# Most common English words compiled by Peter Norvig with data from Google
$ pkg=en_wordcount_web-0.1.0/en_wordcount_web-0.1.0-py3-none-any.whl
$ pip install $base/$pkg   # byexample: +pass

# Most common Trigrams compiled by Peter Norvig with data from Google
$ pkg=en_wordcount_trigrams-0.1.0/en_wordcount_trigrams-0.1.0-py3-none-any.whl
$ pip install $base/$pkg   # byexample: +pass
```

Wordsiv auto-discovers these installed packages, and and can use these sources
right away. Let's try a source with the most common words in the English
language in modern usage:

```python
>>> from wordsiv import WordSiv
>>> wsv = WordSiv()
>>> wsv.sent(source='en_wordcount_web')
('Maple canvas sporting pages transferred with superior government brand with '
 'women for key assign.')
```

## Models

How does a Wordsiv know how to arrange words from a Source into a sentence? This
is where **Models** come into play.

The source `en_wordcount_web` uses model `rand` by default. Here we explicitly
select the model `rand` to achieve the same result as above:

```python
>>> wsv = WordSiv()
>>> wsv.sent(source='en_wordcount_web', model="rand")
('Maple canvas sporting pages transferred with superior government brand with '
 'women for key assign.')
```

Notice we get the same sentence when we initialize a new WordSiv() object. This
is because Wordsiv is [designed to be determinisic](#determinism).

### Markov Model

If we want text that is somewhat natural-*looking*, we might use our
[MarkovModel][markov-model] (`model='mkv'`).

```python
>>> wsv.para(source="en_markov_gutenberg", model="mkv") # byexample: +skip
"Why don't think so desirous of hugeness. Our pie is worship..."
```

A [Markov model](https://en.wikipedia.org/wiki/Markov_model) is trained on real
text, and forecasts each word by looking at the preceding word(s). We keep the
model as stupid as possible though (one word state) to generate as many
different sentences as possible.

### WordCountSource Models

[WordCountSource][wordcount-model] Sources and Models work with simple lists of words
and occurence counts to generate words.

The [WordProbModel][random-model] (`model='rand'`) uses occurence counts to
randomly choose words, favoring more popular words:

```python
# Default: probability by occurence count
>>> wsv.para(source='en_wordcount_web', model='rand') # byexample: +skip
'Day music, commencement protection to threads who and dimension...'
```

The **WordProbModel** can also be set to ignore occurence counts and choose words
completely randomly:

```python
>>> wsv.sent(source='en_wordcount_web', num_words=5, prob=False) # byexample: +skip
'Conceivably championships consecration ects— anointed.'
```

The [SequentialModel][sequential-model] (`model='seq'`) spits out words in the
order they appear in the Source. We could use this Model to display the top 5
trigrams in the English language:

```python
>>> wsv.words(source='en_wordcount_trigrams', num_words=5) # byexample: +skip
['the', 'ing', 'and', 'ion', 'tio']
```


### Change Case

Both the [MarkovModel][markov-model] and [WordCountSource][wordcount-model] models
allow us to uppercase or lowercase text, whether or not the source words are
capitalized or not:

```python
>>> wsv = WordSiv()
>>> wsv.sent('en_wordcount_web', uc=True, max_num_words=8)
'MAPLE CANVAS SPORTING PAGES TRANSFERRED, WITH SUPERIOR GOVERNMENT.'

>>> wsv.sent(
...    'en_markov_gutenberg', lc=True, min_num_words=7, max_num_words=10
... )
'i besought the bosom of the sun so'
```

The [WordProbModel][random-model] by capitalizes sentences by default, but we can
turn this off:

```python
>>> wsv.sent('en_wordcount_web', cap_sent=False, num_words=10)
'egcs very and mortgage expressed about and online truss controls.'
```

### Punctuation

By default the [WordCountSource][wordcount-model] models insert punctuation with
probabilities roughly derived from usage in the English language.

We can turn this off by passing our own function for punctuation:

```python
>>> def only_period(words, *args): return ' '.join(words) + '.'
>>> wsv.para(
...    source='en_wordcount_web', punc_func=only_period, num_words=5, para_len=2
... )
'By schools sign I avoid. Or about fascism writers what.'
```

For more details on `punc_func`, see [punctuation.py](./wordsiv/punctuation.py).
This only applies for [WordCountSource][wordcount-model] models, as the
[MarkovModel][markov-model] uses the punctuation in it's source data.

### Sentence and Word Parameters

[Models](#models) take care of generating *sentences* and *words*, so parameters
relating to these are handled by the models. For now, please refer to the source
code for these models to learn the parameters accepted for `word()`, `words()`,
and `sent()` APIs:

- [Random Model][random-model]
- [Sequential Model][sequential-model]
- [Markov Model][markov-model]

### Paragraph and Text Parameters

The **WordSiv** object itself handles `sents()`, `para()`,
`paras()` and `text` calls with their parameters. See the [WordSiv
Class][wordsiv-object] source code to learn how to customize the text output.

## Technical Notes

### Determinism

When proofing type, we probably want our proof to stay the same as long as we
have the same character set. This helps us compare changes in the type.

For this reason, Wordsiv uses a single
[pseudo-random](https://docs.python.org/3/library/random.html) number generator,
that is seeded upon creation of the WordSiv object. This means that a Python
script using this library will produce the same outcome wherever it runs.

If you want your script to generate different words, you can seed the WordSiv
object:

```python
>>> wsv = WordSiv(seed=6)
>>> wsv.sent(source="en_markov_gutenberg", min_num_words=7)
'even if i forgot the go in their'
```

## Similar Tools

I'm definitely not the first to generate words for proofing. Check out these
cool projects, And let me know if you know of more I should add!

- **[word-o-mat][word-o-mat]**: Nina
  Stössinger's RoboFont extension for making test words. Also ported to
  [Glyphs](https://github.com/schriftgestalt/word-o-mat) and
  [Javascript](https://github.com/kennethormandy/word-o-mat).
- **[adhesiontext](https://adhesiontext.com)**: a web-based tool by Miguel Sousa
  for generating text from a limited character set.

## Acknowledgements

I probably wouldn't have got very far without the inspiration of [word-o-mat],
and a nice [DrawBot](https://www.drawbot.com/) script that [Rob
Stenson](https://robstenson.com/) shared with me. The latter is where I got the
idea to [seed the random number generator](#determinism) to make it
deterministic.

Also want to thank my wife Pammy for kindly listening as I explain each
esoteric challenge I've tackled, and lending me emotional support when I almost
wiped out 4 hours of work with a careless Git mistake.

[markov-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/algorithms/markov.py#L46
[wordcount-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/algorithms/wordcount.py#L108
[random-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/algorithms/wordcount.py#L108
[sequential-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/algorithms/wordcount.py#L249
[word-o-mat]: https://github.com/ninastoessinger/word-o-mat
[wordsiv-object]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/__init__.py#L132
[drawbot]: https://www.drawbot.com
[releases]: https://github.com/tallpauley/wordsiv-source-packages/releases
[source-packages]: https://github.com/tallpauley/wordsiv-source-packages
