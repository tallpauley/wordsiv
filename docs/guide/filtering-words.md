# Filtering Words

## Filter Words by Letter Case

The most important parameter in WordSiv (for bicameral languages) is `case`.
WordSiv allows for words in Vocabs to be:

- **lowercase** (e.g. `"owl"`): **`lc`**
- **capitalized** (e.g. `"Korea"`): **`cap`**
- **all caps** (e.g. `"WWF"`): **`uc`**
- **camel-case** (e.g. `"DDoS"`): (no parameter, but respected)

The `case` argument allows you to select the desired output letter case
(considering your glyph set, if you've set `glyphs`), optionally transforming
the original case of words from the Vocab.

The options are best demonstrated with a small example Vocab:
```python
--8<-- "case-demo.py"
```

### Default: Any Case with Transforms (`case='any'`)

The default option (`case='any'`) tries to match as many words as possible,
transforming the case to `cap` and then `uc` if there aren't any matches.

```python
--8<-- "case-any.py"
```

### Any Case without Transforms (`case='any_og'`)

You can also specify you want any word *exactly* as it appears
in the Vocab `case='any_og'`:

```python
--8<-- "case-any-og.py"
```

### Lowercase (`case='lc'`)

The `lc` option selects lowercase words from the Vocab, like "bread". No words
that are all caps or uppercase in the Vocab will be returned (it will NOT
include "paris" or "fda").

!!! Note "Why no `lc_og`?"
    There is no `lc_og` option since `lc` already only uses lowercase words from
    the Vocab.

```python
--8<-- "case-lc.py"
```

### Lowercase, Force Transforms (`case='lc_force'`)

The `lc_force` option selects all words from the Vocab, and indiscriminately
transforms them to lowercase.

```python
--8<-- "case-lc-force.py"
```

### Capitalized (`case='cap'`)

The `cap` option selects capitalized words from the Vocab (like "Paris") as well as
lowercase words from the Vocab, transformed to capitalized (like "Boat").

```python
--8<-- "case-cap.py"
```

### Capitalized, Force Transforms (`case='cap_force'`)

The `cap_force` option selects all words from the Vocab, and indiscriminately
transforms them to uppercase.

```python
--8<-- "case-cap-force.py"
```

### Capitalized without Transforms (`case='cap_og'`)

The `cap_og` option selects capitalized words from the Vocab (like "Paris"). It does
**not** transform any lowercase words from the Vocab to capitalized. This is
useful for getting words like proper nouns.

```python
--8<-- "case-cap-og.py"
```

### All Caps (`case='uc'`)

The `uc` option selects all caps words from the Vocab (like "WWF"), as well as
lowercase and capitalized words from the vocab, transformed to all caps
(like "PARIS" and "BOAT").

```python
--8<-- "case-uc.py"
```

### All Caps without Transforms (`case='uc_og'`)

The `uc_og` option selects all caps words from the Vocab (like "WWF"). It does
**not** transform any lowercase or capitalized words to all caps. This is
useful for getting all caps words like acronyms.

```python
--8<-- "case-uc-og.py"
```

### All Caps, Force Transforms (`case='uc_force'`)

The `uc_force` option selects all words from the Vocab, and indiscriminately
transforms them to uppercase.

```python
--8<-- "case-uc-force.py"
```
