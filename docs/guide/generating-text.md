# Generating Text

WordSiv provides several methods for generating text at different levels:

- Word(s): [`word()`](#random-word-generation-word),
  [`words()`](#list-of-random-words-words),
  [`top_word()`](#most-common-word-top_word),
  [`top_words()`](#list-of-most-common-words-top_words)
- Sentence(s): [`sent()`](#sentence-sent), [`sents()`](#list-of-sentences-sents)
- Paragraph(s): [`para()`](#paragraph-generation-para),
  [`paras()`](#multiple-paragraphs-generation-paras)
- Text Blocks: [`text()`](#full-text-block-generation-text)

## Text Generation Methods

WordSiv is structured so that word generation calls cascade, passing arguments
from the larger to smaller text generation methods. So when you call `text()`:

- `text()` calls `paras()`, joining the list items into a string
- `paras()` calls `para()` multiple times, returning results in a list
- `para()` calls `sents()`, joining the list items into a string
- `sents()` calls `sent()` multiple times, returning results in a list
- `sent()` calls `words()`, joining the list items into a string
- `words()` calls `word()` multiple times, returning results in a list

This means you can pass arguments to `text()` that will effect all the smaller
text generation methods it calls:

```python
--8<-- "text-propagation.py"
```

### Random Word (`word()`)

The `word()` method generates a single random word based on word frequencies.
Accepts [word filter arguments](../filtering-words).

```python
--8<-- "word.py"
```

### Most Common Word (`top_word()`)

The `top_word()` method retrieves the most common word or the nth common word.
Accepts [word filter arguments](../filtering-words).

```python
--8<-- "top-word.py"
```

### List of Random Words (`words()`)

The `words()` method generates multiple random words using word frequencies. See
also [word filter arguments](../filtering-words).

```python
--8<-- "words.py"
```

### List of Most Common Words (`top_words()`)

The `top_words()` method generates a list of the most common words in descending
frequency order. Accepts [word filter arguments](../filtering-words).

```python
--8<-- "top-words.py"
```

### Sentence (`sent()`)

The `sent()` method generates a single sentence by calling `words()` and
optionally adding punctuation. Accepts [word filter
arguments](../filtering-words).

```python
--8<-- "sent.py"
```

### List of Sentences (`sents()`)

The `sents()` method generates multiple sentences and returns them in a list.
Accepts [word filter arguments](../filtering-words).

```python
--8<-- "sents.py"
```

### Paragraph (`para()`)

The `para()` method generates a single paragraph by joining sentences. Accepts
[word filter arguments](../filtering-words).

```python
--8<-- "para.py"
```

### Multiple Paragraphs (`paras()`)

The `paras()` method generates multiple paragraphs and returns them in a list.
Accepts [word filter arguments](../filtering-words).

```python
--8<-- "paras.py"
```

### Text Block (`text()`)

The `text()` method generates a full text block by joining paragraphs. Accepts
[word filter arguments](../filtering-words).

```python
--8<-- "text.py"
```

## Adjusting Randomness

### Repeatable Output

For reproducible results, you can set a random seed either when initializing
WordSiv or for individual function calls. This is essential if you want you want
your proof to remain the same until you make changes to the code (or your
glyphs).

```python
--8<-- "repeatable-output.py"
```

### Word Randomness (`rnd`)

The `rnd` parameter controls how random the word generation is. This is useful
for getting more less frequent words, especially when your glyph set is limited
and the probability distribution becomes even more skewed towards short, common
words.

- `rnd=0`: Use word frequencies to select words (default)
- `rnd=1`: Completely random word selection
- `0<rnd<1`: Interpolation of word frequency distribution and fully random
  distribution

```python
--8<-- "rnd.py"
```

### Punctuation Randomness (`rnd_punc`)

The `rnd_punc` parameter controls how random the punctuation generation is:

- `rnd=0`: Use punctuation frequencies to select punctuation (default)
- `rnd=1`: Completely random punctuation choice
- `0<rnd<1`: Interpolation of punctuation frequency distribution and fully
  random distribution

```python
# Random punctuation distribution
print(wsv.para(rnd_punc=1))
```

## Advanced Features

### Limiting Word Pool (`top_k`)

You can restrict word selection to the most common `top_k` words. This is useful
if you want to inspect a bunch of highly frequent words.

```python
--8<-- "top-k.py"
```

### Mixing In Numbers (`numbers`)

You can include basic random figures in your text (constrained by `glyphs`) with
the `numbers` parameter.

```python
--8<-- "numbers.py"
```

### Disabling Punctuation (`punc`)

You can disable punctuation with the `punc` parameter:

```python
--8<-- "punc-false.py"
```
