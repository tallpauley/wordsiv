# WordSiv

WordSiv is a Python library for generating proofing text for an incomplete typeface using word probabilities.

Say you've drawn `HAMBUGERFONTSIVhambugerfontsiv.,` and want a sentence with *only* those glyphs:

```python
from wordsiv import sent

my_glyphs = 'HAMBUGERFONTSIVhambugerfontsiv.,'
sent(vocab="en", glyphs=my_glyphs, rnd=.03) # rnd lets us turn up the randomness
```

This returns:

>Bears run saint that fighting bargain remove, genre MA Barbara registration the bug it others entering Steven.

## Key Features

- **Generate text from word probabilities**: Using word occurence counts, WordSiv generates text that is roughly the *shape* of the desired language, just nonsensical!
- **Filter words based on available glyphs**: WordSiv selects words that can be spelled with the glyphs you're ready to display. Add additional word requirements, such as word length, substrings, and regular expressions without worrying about getting 
- **Respects case**: WordSiv respects the case of source words, and filters these via your glyph set. There are sensible defaults so that capitalized words like "Paris" and uppercased words like "IMDB" don't get lowercased unless you explicitly ask for them to be. It also has support for unicameral (single case) languages such as Arabic.
- **Punctuates with probability**: WordSiv uses punctuation probabilities (specific to the language) to insert punctuation throughout generated text.
- **Deterministic**: Using the `seed` parameter, you can ensure you get the same output while your DrawBot script remains the same.
- **Customizable**: You can blend in more randomness to the probability, specificy minimum and maximum word/sentence/paragraph lengths, and much much more.
- **Designed for DrawBot**: WordSiv is has been (re)designed to be used in DrawBot and now features easy module-level APIs like `word()`, `sentence()`, `paragraph()`. If you favor a more object-oriented approach you can still work with `WordSiv` objects directly.

## Why Simple Word Probability?

Proofing text doesn't necessarily have to be syntactically correct or have meaning. It just needs the right amount of common and uncommon words to give it a "realistic" *shape*. Often type designers do this manually, such as in Jonathan Hoefler's fantastic [proof](https://jonathanhoefler.com/articles/how-to-proof-a-typeface):
>Finally, I wanted the text to have the visual cadences of my native English, in which words of variable but digestible length are punctuated by shorter ones.

If we simply select words randomly, out of a hat which contains many more duplicates of say, "the" than "etymology", we'll get a string of words which visually resembles a sentence. This is how WordSiv works: sampling words from a *probability distribution* which is determined by the occurence counts of words in a corpus of text.

Of course, the more we restrict our glyph set the more we've tampered with the natural distribution of words, since most the longer, less-common words aren't available (which make up the long tail of the [Zipf distribution](https://en.wikipedia.org/wiki/Zipf's_law#Word_frequencies_in_natural_languages)). However, we can blend in a bit of randomness to make it look like real text at a glance!

This might be *more fun* [with LLMs](#other-resources), because the glyph-limited text could potentially be both grammatically and semantically correct. However, it remains to be seen if stability can be achieved while filtering out the majority of tokens. And more importantly, why spend so much more compute for so little payoff?

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