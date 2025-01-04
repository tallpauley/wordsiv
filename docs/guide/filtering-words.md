# Filtering Words

## Letter Case

The most important parameter in WordSiv (for bicameral languages) is `case`.
WordSiv allows for words in Vocabs to be:

- **lowercase** (e.g. `"owl"`): **`lc`**
- **capitalized** (e.g. `"Korea"`): **`cap`**
- **all caps** (e.g. `"WWF"`): **`uc`**
- **camel-case** (e.g. `"DDoS"`): (no parameter, but respected)

The `case` argument allows you to:

- select words from a Vocab which **already have the desired case** and only
  contain `glyphs`:  **`lc`**, **`cap_og`**, **`uc_og`**
- select words from a Vocab which **can be transfomed into the desired case**
  and *still only contain* `glyphs`: **`uc`**, **`cap`**, **`cap_force`**,
  **`lc_force`**
- select any word from a Vocab **of any case** which only contain `glyphs`:
  **`any-og`**
- select words from a Vocab **of any case** which only contain `glyphs`,
  transforming case to `cap` and then `uc` if there aren't enough matches:
  **`any`**

The existing letter case is respected, so you have to explicitly specify a case
option if you want to make a change to the case that is unusual, such as:

- Changing `"WWF"` to `"Wwf"` (`cap-force`)
- Changing `"DDoS"`to `"ddos"` (`lc-force`)

### Default: Any Case w/ Expansion (`case='any'`)

The default option tries to match as many words as possible, trying transforming
the case to `cap` and then `uc` if there aren't enough matches.

```python
from wordsiv import set_vocab, sent, top_words

set_vocab('en')

# By default case=`any`

```

### All Caps (`case='uc'`)

```python
sent(case="uc", n_words=5)

# Returns: 'THE PRESS–NOT GET GROWTH.'

# get top 5 words from vocab and capitalize them (if either lc or capitalized)

top_words(case="cap", n_words=5)

# Returns: ['The', 'Of', 'And', 'To', 'A']

# get top words that are *already* capitalized in the vocab

top_words(case="cap_og", n_words=5)

# Returns:  ['I', 'Jan', 'January', 'American', 'John']

```
