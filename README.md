[![CI](https://github.com/tallpauley/wordsiv/actions/workflows/ci.yml/badge.svg)](https://github.com/tallpauley/wordsiv/actions/workflows/ci.yml) [![Coverage Status](https://coveralls.io/repos/github/tallpauley/wordsiv/badge.svg?branch=main)](https://coveralls.io/github/tallpauley/wordsiv?branch=main)

# Wordsiv

Wordsiv is a Python package for generating text with a limited character set. It
is designed for [type proofing](https://ohnotype.co/blog/proof-it), but it may
be useful for generating [lipograms](https://en.wikipedia.org/wiki/Lipogram).

Let's say you have the letters `HAMBURGERFONTSIVhamburgerfontsiv` and
punctuation `.,` in your font. Wordsiv might generate the following drivel:

> True enough, for a fine enough to him at the thrones above, some time for at
> that first the business. She is that he hath set as a thought he even from its
> substratums It is the rest of it is not the things the savings of a movement
> that he measures about the matter, Ahab gives to the boats at noon, or from
> the Green Forest, this high as on Ahab.

## Why Wordsiv?

While designing a typeface, it is useful to examine text with a partial
character set. Wordsiv tries its best to generate realistic-*looking* text with
whatever glyphs are available.

### Wordsiv can do things like...

- Determine available glyphs from a font file
- Generate sorta-realistic-*looking* text with a variety of models
- Filter words by number of characters and approximate rendered width

### Wordsiv hopes to:

- be an easy-to-use and easy-to-extend meaningless language generation framework
- support many languages and scripts (please help me!)

### Wordsiv is NOT

- A realistic langauge generator
- A [responsible human forming sentences](#ethical-guidelines)

## Installation

First, install wordsiv with pip:

```bash
# we install straight from git (for now!)
$ pip install git+https://github.com/tallpauley/wordsiv # byexample: +pass
```

Next, install one or more source packages from the [releases
page](https://github.com/tallpauley/wordsiv-source-packages/releases) of the
[wordsiv-source-packages](https://github.com/tallpauley/wordsiv-source-packages)
repo:

```bash
$ base=https://github.com/tallpauley/wordsiv-source-packages/releases/download
$ pkg=en_markov_gutenberg-0.1.0/en_markov_gutenberg-0.1.0-py3-none-any.whl
$ pip install $base/$pkg # byexample: +pass
```

Now you can make bogus sentences in Python!

```python
>>> import wordsiv
>>> wsv = wordsiv.WordSiv(limit_glyphs=('HAMBURGERFONTSIVhamburgerfontsiv'))
>>> wsv.sentence(source='en_markov_gutenberg')
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
>>> wsv.sentence(source='en_wordcount_web')
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
>>> wsv.sentence(source='en_wordcount_web', model="rand")
('Maple canvas sporting pages transferred with superior government brand with '
 'women for key assign.')
```

Notice we get the same sentence when we initialize a new WordSiv() object. This
is because Wordsiv is [designed to be determinisic](#determinism).

### Markov Model

If we want text that is somewhat natural-*looking*, we might use our
[MarkovModel][markov-model] (`model='mkv'`).

```python
>>> wsv.paragraph(source="en_markov_gutenberg", model="mkv") # byexample: +skip
"Why don't think so desirous of hugeness. Our pie is worship..."
```

A [Markov model](https://en.wikipedia.org/wiki/Markov_model) is trained on real
text, and forecasts each word by looking at the preceding word(s). We keep the
model as stupid as possible (one word state) to generate as many different
sentences as possible.

### WordCount Models

[WordCount][wordcount-model] Sources and Models work with simple lists of words
and occurence counts to generate words.

The [RandomModel][random-model] (`model='rand'`) uses occurence counts to
randomly choose words, favoring more popular words:

```python
# Default: probability by occurence count
'Day music, commencement protection to threads who and dimension...'
```

The **RandomModel** can also be set to ignore occurence counts and choose
completely randomly:

```python
>>> wsv.sentence(source='en_wordcount_web', sent_len=5, prob=False) # byexample: +skip
'Conceivably championships consecration ects— anointed.'
```

The [SequentialModel][sequential-model] (`model='seq'`) spits out words in the
order they appear in the Source. We could use this Model to display the top 5
trigrams in the English language:

```python
>>> wsv.words(source='en_wordcount_trigrams', num_words=5) # byexample: +skip
['the', 'ing', 'and', 'ion', 'tio']
```

## Limiting Glyphs

### Limiting Glyphs with a Font File

Wordsiv is built around the idea of selecting words which can be rendered with
the *glyphs* in an incomplete font file. WordSiv can automatically determine
what glyphs are in a font file.

Let's load a font with the characters `HAMBURGERFONTSIVhamburgerfontsiv`

```python
>>> wsv = WordSiv(font_file='tests/data/noto-sans-subset.ttf')
>>> wsv.sentence(source='en_markov_gutenberg', max_sent_len=10)
'Nor is fair to be in as these annuities'
```

### Limiting Glyphs Manually

We can do the same thing, by using the `limit_glyphs` parameter manually.

```python
>>> wsv = WordSiv(limit_glyphs='HAMBURGERFONTSIVhamburgerfontsiv')
>>> wsv.sentence(source='en_wordcount_web')
'Manage miss ago are motor to rather at first to be of has forget'
```

### Limiting Glyphs with `font_file` AND `limit_glyphs`

It can be useful at times to specify the character set we *want to display*, and
only using those characters if we have them in the font file. We can do
this by specifying both `font_file` and `limit_glyphs`:

```python
>>> wsv = WordSiv(
...    font_file='tests/data/noto-sans-subset.ttf',
...    limit_glyphs='abcdefghijklmnop'
... )
>>> wsv.sentence('en_wordcount_web', cap_sent=False, min_wl=3)
'eng gnome gene game egg one aim him again one game one image boom'
```

## Customizing Text

There are a variety of ways text can be manipulated. Here are some examples:

### Change Case

Both the [MarkovModel][markov-model] and [WordCount][wordcount-model] models
allow us to uppercase or lowercase text, whether or not the source words are
capitalized or not:

```python
>>> wsv = WordSiv()
>>> wsv.sentence('en_wordcount_web', uc=True, max_sent_len=8)
'MAPLE CANVAS SPORTING PAGES TRANSFERRED, WITH SUPERIOR GOVERNMENT.'

>>> wsv.sentence(
...    'en_markov_gutenberg', lc=True, min_sent_len=7, max_sent_len=10
... )
'i besought the bosom of the sun so'
```

The [RandomModel][random-model] by capitalizes sentences by default, but we can
turn this off:

```python
>>> wsv.sentence('en_wordcount_web', cap_sent=False, sent_len=10)
'egcs very and mortgage expressed about and online truss controls.'
```

### Punctuation
Notice that in the preceding example we got quotes? This comes from the default
punctuation function and probabilities for punctuation in the given langauge
of the source.

We can turn this off by passing our own function for punctuation:
```python
>>> def only_period(words, *args): return ' '.join(words) + '.'
>>> wsv.paragraph(
...    source='en_wordcount_web', punc_func=only_period, sent_len=5, para_len=2
... )
'By schools sign I avoid. Or about fascism writers what.'
```

For more details on `punc_func`, see [punctuation.py](./wordsiv/punctuation.py).
This only applies for [WordCount][wordcount-model] models, as the
[MarkovModel][markov-model] uses the punctuation in it's source data.

### Sentence and Word Parameters

[Models](#models) take care of generating *sentences* and *words*, so parameters
relating to these are handled by the models. For now, please refer to the source
code for these models to learn the parameters accepted for `word()`, `words()`,
and `sentence()` APIs:

- [Random Model][random-model]
- [Sequential Model][sequential-model]
- [Markov Model][markov-model]

### Paragraph and Text Parameters

Wordsiv itself takes care of formatting everything beyond the sentence. See the
source code for the [WordSiv Class][wordsiv-object] to learn the parameters for
`sentences()`, `paragraph()`, `paragraphs()` and `text()`.

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
>>> wsv.sentence(source="en_markov_gutenberg", min_sent_len=6)
'even if i forgot the go in their'
```

## Ethical Guidelines

After watching the documentary [Coded Bias](https://www.imdb.com/title/tt11394170/), I considered whether we should even generate text based on historical (or even current) data, because of the sexism, racism, colonialism, homophobia, etc., contained within the texts.

This section attempts to address some of these ethical questions that arose for me (Chris Pauley), and try to steer this project away from generating offensive text.

### Intentions

First off, this library was designed for the purposes of:

- generating text that isn't intended to be *read*, just *looked at*:
- **type design proofing**: in which we are examining how words, sentences, and paragraphs *look*.

Of course, we naturally *read* words (duh), so it goes without saying that you should supervise text generated by this library.

### Ethical Random Text Generation?

I considered if there were more progressive texts I could train a Markov model on. However, we are scrambling the source text to meaninglessness anyway, to maximize sentences made with a limited character set.

Even the most positive text can get dark really quick when scrambled. A Markov model of state size 1 (ideal for limited character sets) trained with the [UN Universal Declaration of Human Rights](https://www.un.org/en/about-us/universal-declaration-of-human-rights) made this sentence:

```text
Everyone is entitled to torture
or other limitation of brotherhood.
```

The point is, semi-random word generation ruins the meaning of text, so why bother picking a thoughtful source? However, we should really try to stay away from offensive source material, because offensive patterns **will** show up if there is any probability involved.

### Ethical Guidelines for Contributing Sources and Models

If you're wanting to contribute a source and/or model to this project, here are some guidelines:

#### Generate sentences that are largely [nonsensical](https://en.wikipedia.org/wiki/Nonsense)

For example, we keep MarkovModel from picking up too much context from the original text by keeping a state size of 1. Having a single word state also increases the amount of potential sentences as well, so it works out.

The sentences we generate make less sense, but since this is designed for dummy text for proofing, this is a good thing!

#### Try to filter sources of "generally offensive" words

It's tricky filtering out "offensive" words, since:

- the offensiveness of words depends on context
- offensiveness is largely subjective
- "offensive" word lists could potentially be used to silence important discussions

Since we're generating nonsensical text for proofing, we should try our best to filter wordlists by [offensive](https://github.com/reimertz/curse-words) [words](https://github.com/MauriceButler/badwords) [lists](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/). If you really need swears in your text, you can always add them back in to sources for your own purposes.

We can't prevent random words from forming offensive sentences, but we can at least restrict some words that *tend to form* offensive sentences.

#### Stay away from offensive sources

Statistical models like those used in WordSiv will pick up on patterns in text— especially [MarkovModels](#markov-model). Try to pick source material that is fairly neutral (not that anything *really* is).

I trained [en_markov_gutenberg](https://github.com/tallpauley/wordsiv-source-packages/releases/tag/en_markov_gutenberg-0.1.0) with these public domain texts from [nltk](https://www.nltk.org/book/ch02.html), which seemed safe enough for a dumb, single-word-state Markov model:

```
['austen-emma.txt', 'austen-persuasion.txt', 'austen-sense.txt',
'blake-poems.txt', 'bryant-stories.txt', 'burgess-busterbrown.txt',
'carroll-alice.txt', 'chesterton-ball.txt', 'chesterton-brown.txt',
'chesterton-thursday.txt', 'edgeworth-parents.txt', 'melville-moby_dick.txt',
'milton-paradise.txt', 'shakespeare-caesar.txt', 'shakespeare-hamlet.txt',
'shakespeare-macbeth.txt', 'whitman-leaves.txt']
```

If you notice any particular models generating offensive sentences more than not, please file an issue at the [wordsiv-source-packages](https://github.com/tallpauley/wordsiv-source-packages/issues) repo.

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

I also borrowed heavily from [spaCy](https://spacy.io) in how I set up
the [Source packages](https://github.com/tallpauley/wordsiv-source-packages/).

Also want to thank my wife Pammy for kindly listening as I explain each
esoteric challenge I've tackled, and lending me emotional support when I almost
wiped out 4 hours of work with a careless Git mistake.

[markov-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/sentence_models_sources/markov.py#L46
[wordcount-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/sentence_models_sources/wordcount.py#L108
[random-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/sentence_models_sources/wordcount.py#L108
[sequential-model]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/sentence_models_sources/wordcount.py#L249
[punc-func]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/sentence_models_sources/wordcount.py#L214
[word-o-mat]: https://github.com/ninastoessinger/word-o-mat
[wordsiv-object]: https://github.com/tallpauley/wordsiv/blob/main/wordsiv/__init__.py#L132