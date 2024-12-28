# Letter Case

WordSiv respects case (with Vocabs that include cased words), and has a single parameter `case` to retrieve and recase words that fit your requirements:

```python
from wordsiv import set_vocab, sent, top_words

set_vocab('en')

sent(case="uc", n_words=5)
# Returns: 'THE PRESS–NOT GET GROWTH.'

# get top 5 words from vocab and capitalize them (if either lc or capitalized)
top_words(case="cap", n_words=5)
# Returns: ['The', 'Of', 'And', 'To', 'A']

# get top words that are *already* capitalized in the vocab
top_words(case="cap_og", n_words=5)
# Returns:  ['I', 'Jan', 'January', 'American', 'John']
```
