[![CI](https://github.com/tallpauley/wordsiv/actions/workflows/ci.yml/badge.svg)](https://github.com/tallpauley/wordsiv/actions/workflows/ci.yml) [![Coverage Status](https://coveralls.io/repos/github/tallpauley/wordsiv/badge.svg?branch=main)](https://coveralls.io/github/tallpauley/wordsiv?branch=main)

# Wordsiv

Wordsiv is a Python library for generating text with a limited character set. The library was designed specifically for [type proofing](https://ohnotype.co/blog/proof-it), but there may be other applications.

**WARNING:** Wordsiv is *very* early in the development/exploration process, and is subject to radical restructuring at this point!

## Why Wordsiv?

When designing a typeface, it is useful to see text (or at least words) set in the type before the character set is complete.

We need a tool that can make realistic-*looking* text with whatever glyphs we have already designed.

## Features

- Generate text given an incomplete font file and/or a specified character set.
- Generate text in a variety of ways, some which are somewhat realistic-*looking* (Markov chains).
- Comes with ready-to-use language data sets for generating text.

## Vision

- Easily extensible & multi-lingual (multi-script??) meaningless language generation
- Easy-to-use Pythonic interface, which allows advanced customization for those interested

## Wordsiv is NOT

- A realistic langauge generator
- A [responsible human forming sentences](#ethical-guidelines)

## Quick Start

First, install wordsiv

```bash
# For now, we install straight from git
$ pip install git+https://github.com/tallpauley/wordsiv  # byexample: +timeout=10 +pass

# TODO: Note to Chris: publish an actual package??
```

Next, you'll need to install one or more source packages from the [tallpauley/wordsiv-source-packages](https://github.com/tallpauley/wordsiv-source-packages/releases) repo:

```bash

$ pip install https://github.com/tallpauley/wordsiv-source-packages/releases/download/en_markov_gutenberg-0.1.0/en_markov_gutenberg-0.1.0-py3-none-any.whl  # byexample: +timeout=10 +pass

# TODO: Note to Chris: Make `wordsiv download` CLI command!

```

Now you are ready to make bogus sentences with Wordsiv in Python!

```python

>>> import wordsiv
>>> wsv = wordsiv.WordSiv(limit_glyphs=('HAMBURGERFONTSIVhamburgerfontsiv'))
>>> wsv.sentence(pipeline='en_markov_gutenberg')
'The strife Of that a brother or I am sure is in an hour or from the Muses'
```

## Similar Tools

- **[adhesiontext](https://adhesiontext.com)**: a web-based tool by Miguel Sousa for generating text from a limited character set.
- **[word-o-mat](https://github.com/ninastoessinger/word-o-mat)**: Nina Stössinger's RoboFont extension for making test words. Also ported to [Glyphs](https://github.com/schriftgestalt/word-o-mat) and [Javascript](https://github.com/kennethormandy/word-o-mat).

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

Theoretically we could train a more sophisticated model on a "forward-thinking" text and get some "forward-thinking" sentences. But it wouldn't work well for our purpose of generating text from a limited character set, and it probably wouldn't be that meaningful anyway.

The point is: **use this library with caution**. Don't publish or share content you haven't looked over.

### Ethical Guidelines for Contributing Models

If you're wanting to contribute a model to this project, here are some guidelines:

#### Generate sentences that are largely [nonsensical](https://en.wikipedia.org/wiki/Nonsense)

When building a Markov model that works best for a small character set (state size of 1), nonsensical sentences were a natural outcome anyway.

#### *Try* to filter wordlists of "generally offensive" words

It's tricky filtering out "offensive" words, since:

- the offensiveness of words depends on context
- offensiveness is largely subjective
- "offensive" word lists could potentially be used to silence important discussions

Since we're generating nonsensical text for proofing, we might as well *try* to filter wordlists by [offensive](https://github.com/reimertz/curse-words) [words](https://github.com/MauriceButler/badwords) [lists](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/).

We can't prevent random words from forming "offensive" sentences, but we can at least restrict some words that *tend to form* "offensive" sentences. You can always add words into your own corpus.
