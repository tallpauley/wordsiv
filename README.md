
# WordSiv

WordSiv is a Python library for generating [proofing](https://ohnotype.co/blog/proof-it) text for an incomplete typeface using word probabilities.

Say you've drawn `'HAMBUGERFONTSIVhambugerfontsiv.,` and want a sentence with *only* those glyphs:

```python
from wordsiv import set_vocab, set_glyphs, sent

set_vocab('en')
set_glyphs('HAMBUGERFONTSIVhambugerfontsiv.,')

sent(rnd=.03) # rnd lets us turn up the randomness
```

This produces:

```python
'Author the us, Brian native he setting assume emissions brain.'
```

Total nonsense, but highly useful for evaluating an early stage font. You can also use it simply to select random words (or words ranked by occurence) that fit your criteria:

```python
from wordsiv import set_vocab, set_glyphs

# get random matching words
words(vocab="es", glyphs='hambugerfontsivñ', n_words=5, rnd=1, contains='ña')
# Returns: ['foránea', 'náufragos', 'estáis', 'fresán', 'trastámara']

# get most common matching words
top_words(vocab="ar", n_words=5, min_wl=3, glyphs='خشطغب')
# Returns: ['خطب', 'خطط', 'خشب', 'طبخ', 'بخط']
```

## Text from Word Probabilities

Proofing text doesn't necessarily have to be syntactically correct or have meaning. It just needs the right amount of common and uncommon words to give it a "realistic" *shape*. Often type designers do this manually, such as in Jonathan Hoefler's fantastic [proof](https://jonathanhoefler.com/articles/how-to-proof-a-typeface):
>Finally, I wanted the text to have the visual cadences of my native English, in which words of variable but digestible length are punctuated by shorter ones.

If we simply select words randomly, out of a hat which contains many more duplicates of say, "the" than "etymology", we'll get a string of words which visually resembles a sentence!

Of course, the more we restrict our glyph set the more we've tampered with the natural distribution of words, since most the longer, less-common words aren't available (which make up the long tail of the [Zipf distribution](https://en.wikipedia.org/wiki/Zipf's_law#Word_frequencies_in_natural_languages)). However, we can blend in a bit of randomness to make it look like real text at a glance!

This might be *more fun* [with LLMs](#other-resources), because the glyph-limited text could potentially be both grammatically and semantically correct. However, it remains to be seen if stability can be achieved while filtering out the majority of tokens. And more importantly, why spend so much more compute for so little payoff?

## Features

#### Included Words and Probabilities

WordSiv includes "Vocabs": word and punctuation probabilities for English, Spanish, Arabic and Farsi. It can be easily extended to support any language (which I would love to incorporate upstream into this project).

#### Smart Case Handling

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

#### Meaningless Text Generation

WordSiv uses TSV files of words with occurence counts to make text that **looks** realistic:

```python
from wordsiv import set_vocab, para, sent

# no constraints on glyphs
set_vocab('en')
para(n_words=10, n_sents=2)
# Returns: 'Topics out, found students western have (would) of little two. To John be, a for by for the our the will cart me for on.'
```

#### Punctuation

Punctuation occurs with frequencies derived from real texts. However, you can adjust `rand_punc` to make any punctuation occur with equal probability:
```python

from wordsiv import set_vocab, para

# 0 is default (normal probability), 1 is fully random
para(n_words=8, n_sents=2, rnd_punc=0.5)
# Returns: 'Employment; not home project of the body or. Month that will, able questions of “said” I…'
```

#### Word Filtering

#### Tuneable Probabiity

TODO: talk about how we can blend between weighted and fully random

#### Reproduceability

We don't want proofs to change every time we generate them. For this reason, we have the ability to "seed" the random generator at any point to make our output deterministic:

```python
from wordsiv import set_vocab, set_glyphs, sent
set_vocab('en')
set_glyphs('HAMBUGERFONThambugerfont')

# same results
sent(seed=3, rnd=.1)
'Heart tent terra Emma root buffet foam mom Hagen to earth at ammo'
sent(seed=3)
'Heart tent terra Emma root buffet foam mom Hagen to earth at ammo'

# not if we change our glyphs though!
set_glyphs('HAMBUGERFONTSIVhambugerfontsiv')
sent(seed=3)
'Of not but not to as on to setting the of the things'

# you only need to seed at the beginning of your proof
(word(seed=1), word())
('of', 'agreement')
(word(seed=1), word())
('of', 'agreement')

# so as long as you don't insert a new call
(word(seed=1), word(startswith='f'), word())
('of', 'fee', 'area')
```

## Installation in DrawBot

1. Install the `wordsiv` package via **Python->Install Python Packages**:
     - Enter ```git+https://github.com/tallpauley/wordsiv``` and click **Go!**
     - ***Note:*** you'll probably see lots of red text but it
       should still work just fine

    ![Screenshot of DrawBot "Install Python
    Packages" Window](docs/images/drawbot-install.jpg)

## Examples

## Related Resources

### Software Tools Comparison

| Revocab | Type | Author | Glyphs Filtering | Algorithm | Probability |
| -- | -- | -- | -- | -- | -- |
| [WordSiv](#) | CLI | Chris Pauley | Yes | word probability (for now) | Yes |
| [Galvanized Jets](https://www.galvanizedjets.com/) | web tool | Samarskaya & Partners | No | static text | N/A |
| [adhesiontext.com](https://adhesiontext.com/) | web tool | Miguel Sousa | Yes | random word |  No |
| [word-o-mat](https://github.com/ninastoessinger/word-o-mat) | Robofont & Glyphs plug-in | Nina Stössinger | No | random word | No
| [Just Another Test Text Generator](https://justanotherfoundry.com/generator) | web tool, [CLI](https://github.com/justanotherfoundry/text-generator/tree/master) | Tim Ahrens | Yes | trigram character prediction | Yes |

### Other Resources

| Revocab | Author | Notes |
| -- | -- | -- |
| [How to Proof a Typeface](https://jonathanhoefler.com/articles/how-to-proof-a-typeface) | Jonathan Hoefler | A concise and comprehensive proof of illustrative English words, covering all round/flat spacing trigrams, including bigrams for sentence start/end and 4-grams for repeated letters. Made to look more text-like with joining phrases like "of the".
| [A Simple Way to Program an LLM Lipogram](https://coreyhanson.com/blog/a-simple-way-to-program-an-llm-lipogram/) | Corey Hanson | A really cool example of using LLMs for lipograms.
| [Most Language Models can be Poets too: An AI Writing Assistant and Constrained Text Generation Studio](https://arxiv.org/abs/2306.15926) | Allen Roush, Sanjay Basu, Akshay Moorthy, Dmitry Dubovoy | Another example of filtering the output of an LLM for lipogram generation and more.
