# Filtering Words

WordSiv provides options for filtering the words that are used
to [generate text](generating-text.md):

- **Letter Case: [`case`](#filter-words-by-letter-case)**
- **Word Length: [`wl`](#filter-words-by-word-length), [`min_wl`](#filter-words-by-word-length), [`max_wl`](#filter-words-by-word-length)**
- **Substrings: [`startswith`](#word-starts-with-string-startswith), [`endswith`](#word-ends-with-string-endswith), [`contains`](#word-contains-strings-contains), [`inner`](#word-contains-inner-strings-inner)**
- **Regular Expressions: [`regexp`](#filter-words-by-regex)**

We demonstrate these arguments with `top_words()` so you can see what's
happening without randomization. You can use these arguments for `word()`,
`words()`, `top_word()`, `top_words()`, `sent()`, `sents()`, `para()`,
`paras()`, `text()`.


## Filter Words by Letter Case

The most important parameter in WordSiv (for bicameral languages) is `case`.
WordSiv allows for words in Vocabs to be:

- **lowercase** (e.g. `"owl"`): **`lc`**
- **capitalized** (e.g. `"Korea"`): **`cap`**
- **all caps** (e.g. `"WWF"`): **`uc`**
- **camel-case** (e.g. `"DDoS"`): (no parameter, but respected)

The `case` argument allows you to select the *desired letter case* while
considering your available glyphs (if you've set `glyphs`), optionally
*transforming the original case* of words from the Vocab to expand results.

The options are best demonstrated with a small example Vocab:
```python
--8<-- "case-demo.py"
```

### Default: Smart Any Case (`case='any'`)

The default option (`case='any'`) tries to match as many words as possible,
first trying `any_og`, then `cap`, then `uc` if there are not any matches.

```python
--8<-- "case-any.py"
```

### Any Case (`case='any_og'`)

The `any_og` option selects any word from the Vocab that can be spelled with
`glyphs` (if set, otherwise all words). It does *not* change the case of words
from the vocab.

```python
--8<-- "case-any-og.py"
```

### Lowercase (`case='lc'`)

The `lc` option selects lowercase words from the Vocab (e.g. `"bread"`). It will
*not* try to lowercase any words with capitals, since we wouldn't want to
lowercase words like `"Paris"`, `"FAA"`, or `"DDoS"`

!!! Note "Why no `lc_og`?"
    There is no need for a `lc_og` option, because `lc` **already** only selects
    lowercase words from the Vocab.
```python
--8<-- "case-lc.py"
```

### Forced Lowercase (`case='lc_force'`)

The `lc_force` option selects all words from the Vocab, and indiscriminately
transforms them to lowercase.

```python
--8<-- "case-lc-force.py"
```

### Capitalized (`case='cap'`)

The `cap` option selects capitalized words from the Vocab (e.g. `"Paris"`) as
well as lowercase (e.g. `"boat"`) words from the Vocab, capitalizing them
(e.g. `"Paris", "Boat"`).

```python
--8<-- "case-cap.py"
```

### Capitalized, No Case Change  (`case='cap_og'`)

The `cap_og` option selects capitalized words from the Vocab (like `"Paris"`).
It does **not** capitalize any lowercase words (like `case='cap'` does). This is
useful for getting capitalized words like proper nouns.

```python
--8<-- "case-cap-og.py"
```

### Forced Capitalized (`case='cap_force'`)

The `cap_force` option selects all words from the Vocab, and indiscriminately
transforms them to uppercase.

```python
--8<-- "case-cap-force.py"
```

### All Caps (`case='uc'`)

The `uc` option selects all caps words from the Vocab (e.g. `"WWF"`), as well as
lowercase (e.g. `"boat"`) and capitalized (e.g. `"Paris"`) words from the
vocab, transforming them to all caps (e.g. `"WWF", "BOAT", "PARIS"`).

```python
--8<-- "case-uc.py"
```

### All Caps, No Case Change (`case='uc_og'`)

The `uc_og` option selects all caps words from the Vocab (e.g. `"WWF"`). It
does **not** capitalize any lowercase or capitalized words (like `case='uc'`
does). This is useful for getting all caps words like acronyms.

```python
--8<-- "case-uc-og.py"
```

### Forced All Caps (`case='uc_force'`)

The `uc_force` option selects all words from the Vocab, and indiscriminately
transforms them to uppercase.

```python
--8<-- "case-uc-force.py"
```

## Filter Words by Word Length

Arguments `wl`, `min_wl`, and `max_wl` let you select for the length of words in
the Vocab:

```python
--8<-- "wl.py"
```

## Filter Words by Substrings

Arguments **[`startswith`](#word-starts-with-string-startswith)**, **[`endswith`](#word-ends-with-string-endswith)**, **[`contains`](#word-contains-strings-contains)**, and **[`inner`](#word-contains-inner-strings-inner)** let you select words which contain specific substrings.

### Word Starts With String (`startswith`)

Argument `startswith` matches words that have a specific glyph/string at the
start of the word, *after* any case transformations may have occurred.

```python
--8<-- "startswith.py"
```

### Word Ends With String (`endswith`)

Argument `endswith` matches words that have a specific glyph/string at the
end of the word, *after* any case transformations may have occurred.

```python
--8<-- "endswith.py"
```

### Word Contains String(s) (`contains`)

Argument `contains` matches words which contain specific string(s) in the word,
*after* any case transformations may have occurred.

```python
--8<-- "contains.py"
```

### Word Contains Inner String(s) (`inner`)
Argument `inner` matches words which contain specific string(s) in `word[1:-1]` (all
but first and last glyphs), *after* any case transformations may have occurred.

```python
--8<-- "inner.py"
```

## Filter Words by Regex
The `regexp` argument lets you match words by regular expression. This filter
happens *after* any case transformations may have occurred. It uses the
[regex](https://pypi.org/project/regex/) library from PyPI which gives more
options for selecting
[unicode blocks](https://www.regular-expressions.info/unicode.html) and more:

```python
--8<-- "regexp.py"
```

## Debugging Filters and Raising Errors

Most of the time when proofing, some output is better than nothing. When WordSiv
can't find a matching word for your `glyphs` and filter arguments, it will just
return an empty string and send a warning log message to the console with some
details. However, we can change these behaviors:

### Suppressing Warning Messages
WordSiv by default outputs log messages when there are no matching words for
the given filters. However, you can turn this off by adjusting the log level:

```python
--8<-- "suppress-warnings.py"
```

### Raising Errors

Maybe you want your script to halt if there are no matching words, or want to
catch the error and try something else. For this you can use the `raise_errors`
option, which will raise `wordsiv.FilterError` if there are no word matches.

```python
--8<-- "raise-errors.py"
```
