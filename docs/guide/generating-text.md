# Generating Text

WordSiv provides several methods for generating text at different levels:

- Word(s): [`word()`](#random-word-generation-word),
  [`words()`](#list-of-random-words-words),
  [`top_word()`](#most-common-word-top_word),
  [`top_words()`](#list-of-most-common-words-top_words)
- Sentence(s): [`sent()`](#sentence-sent),
  [`sents()`](#list-of-sentences-sents)
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
from wordsiv import WordSiv

wsv = WordSiv(vocab='en')

print(
    wsv.text(
        n_paras=3,  # Number of paragraphs
        min_n_sents=2,  # Min sentences per paragraph
        max_n_sents=4,  # Max sentences per paragraph
        min_n_words=3,  # Min words per sentence
        max_n_words=7,  # Max words per sentence
        numbers=0.1,  # 10% chance of numbers
        rnd=0.1,  # 10% random word selection
        rnd_punc=0.5,  # 50% random punctuation
        para_sep="¶",  # Custom paragraph separator
    )
)
```

### Random Word Generation (`word()`)

The `word()` method generates a single random word based on word frequencies:

```python
--8<-- "word.py"
```

### Most Common Word (`top_word()`)

The `top_word()` method retrieves the most common word or the nth common word:

```python
--8<-- "top-word.py"
```

### List of Random Words (`words()`)

The `words()` method generates multiple random words using word frequencies:

```python
--8<-- "words.py"
```

### List of Most Common Words (`top_words()`)

The `top_words()` method generates a list of the most common words in descending frequency order:

```python
--8<-- "top-words.py"
```

### Sentence (`sent()`)

The `sent()` method generates a single sentence by calling `words()` and
optionally adding punctuation:

```python
--8<-- "sent.py"
```

### List of Sentences (`sents()`)

The `sents()` method generates multiple sentences and returns them in a list:

```python
--8<-- "sents.py"
```

### Paragraph Generation (`para()`)

The `para()` method generates a single paragraph by joining sentences:

```python
--8<-- "para.py"
```

### Multiple Paragraphs Generation (`paras()`)

The `paras()` method generates multiple paragraphs and returns them in a list:

```python
--8<-- "paras.py"
```

### Full Text Block Generation (`text()`)

The `text()` method generates a full text block by joining paragraphs:

```python
--8<-- "text.py"
```

## Controlling Randomness

### Repeatable Output

For reproducible results, you can set a random seed either when initializing
WordSiv or for individual function calls:

```python
--8<-- "repeatable-output.py"
```

### Word Selection Randomness (`rnd`)

The `rnd` parameter controls how random the word selection is:

- `rnd=0`: Use word frequencies (default)
- `rnd=1`: Completely random selection
- `0<rnd<1`: Interpolation of word frequency distribution and fully random
  distribution

```python
--8<-- "rnd.py"
```

### Punctuation Selection Randomness (`rnd_punc`)

The `rnd_punc` parameter controls how random the punctuation selection is:

- `rnd=0`: Use punctuation frequencies (default)
- `rnd=1`: Completely random punctuation choice
- `0<rnd<1`: Interpolation of punctuation frequency distribution and fully
  random distribution

```python
# Random punctuation distribution
print(wsv.para(rnd_punc=1))
```

## Advanced Features

### Limiting Word Pool (`top_k`)

Restrict word selection to the most common `top_k` words:

```python
--8<-- "advanced-features.py"
```

### Including Numbers (`numbers`)

Control the probability of including numbers in text:

```python
# 20% chance of including numbers
print(wsv.sent(numbers=0.2))
```

Note that your `glyphs` must include the necessary digits for numbers to appear.

### Disabling Punctuation (`punc`)

You can disable punctuation with the `punc` parameter:

```python
# No punctuation
print(wsv.para(punc=False))
```
