# Release Notes

## 0.2.0 - 2024-12-05

### Added

- Support for Arabic and Farsi (thanks to @jmsole)
- Numbers (which only use digits which are in the glyph set) can be randomly generated with `number()` and interpersed with words via `numbers` parameter for `sent()`, `text()`, etc.
- Probability from word counts can be interpolated with a completely random distribution via the `rnd` parameter.
- `top_word()` and `top_words()` allow for retrieving highly probable words like the former  `SequentialModel`
- English source words have more accurate casing (still needs work though).
- Errors are no longer thrown for filtering out all worlds, UNLESS `throw_errors` parameter is set to `True`. This prevents DrawBot proof generation from being halted by glyph requirements (in conjunction with other parameters) that aren't met yet. These messages are now logged though for debugging!
- Notices/errors are now logged with stdlib, allowing control over how much diagnostic info is displayed

### Fixed

- Performance for filtering is WAY better, using `regex.findall` to rid of Python loops for finding words which work for the glyph set and case requirements.
- Default punctuation probabilities are more reflective of occurence counts in their respective languages (derived via the Leipzig corpora of Wikipedia for now).
- Punctuation dictionaries now properly support Spanish, where `start` and `stop` parameters are now coupled in tuple `wrap_sent`.

### Changed

- CamelCase is always used to refer to WordSiv, including the `WordSiv` class (so it's not read as "Words iv").
- WordSiv method names shortened for ergonomics. `sentence` is `sent`, `paragraph` is `para`, etc.
- Word/probablitiy lists (Vocabs) are now included w/ the WordSiv package for ease of use.
- Word/probability lists (and optionally punctuation) are now encapsulated in "Vocab" objects.
- Instead of having punctuation tuples (formerly named `wrap` in the punct dictionaries) which wrap the entire sentence, these punctuation mark pairs are randomly distributed throughout the sentence. The tuples and their probabilities are now stored in `wrap_inner` in the punctuation dictionaries.

### Removed

- Source packages: added lots of complexity for little benefit. Since we're dialing it back to simple word lists with occurence counts, we no longer anticipate huge files
- Concept of "models". Now all text generation is using a simple probability distribution (no markov)
- Markov sentence generation
- Use of Git LFS
- Font inspection to determine the glyphset: leaving this up the user
- Selecting words based on widths of glyphs in the font
