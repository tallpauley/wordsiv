# Punctuation

Punctuation occurs with frequencies derived from real texts. However, you can adjust `rand_punc` to make any punctuation occur with equal probability:

```python

from wordsiv import set_vocab, para

# 0 is default (normal probability), 1 is fully random
para(n_words=8, n_sents=2, rnd_punc=0.5)
# Returns: 'Employment; not home project of the body or. Month that will, able questions of “said” I…'
```
