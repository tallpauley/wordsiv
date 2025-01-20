## 0.2.1 – 2025-01-20

### Fixed

- minor docs/site issues

## 0.2.0 – 2025-01-20

### Added

- **Built-in "Vocabs"**: Sources are now referred to as **Vocabs**, which
  include English (`"en"`), Spanish (`"es"`), Arabic (`"ar"`), and Farsi
  (`"fa"`) (thanks [@jmsole!](https://github.com/jmsole)).
    - No extra installation required—simply pass `vocab="en"` (etc.) to your
    `WordSiv` methods.
    - English (`"en"`) Vocab features improved capitalization for acronyms,
      proper nouns, and more.
- **Glyphs-aware numeric string generation**: The new `number()` method, plus
  the `numbers` parameter (e.g., `numbers=0.2`) in `words()`, `sent()`, etc.,
  allows digits to appear among words—only digits present in your specified
  glyph set are used.
- **Top-k frequency selection**: Use `top_word()` or `top_words()` to retrieve
  the most common word(s) in frequency order.
    - Replaces the old `SequentialModel`: if you stepped through frequent words,
    call `top_words(n_words=...)` now.
- **Advanced word filtering**: New substring and regex constraints let you
  refine which words appear. In addition to `min_wl`, `max_wl`, and `wl`, you
  can now use (thanks [@jmsole!](https://github.com/jmsole)):
    - `startswith="..."`
    - `endswith="..."`
    - `contains="..."`
    - `inner="..."`
    - `regexp="..."`
- **`raise_errors` parameter**: If set to `True`, WordSiv raises a `FilterError`
  instead of logging a warning when no words match your filters. By default, it
  logs a warning and returns an empty string.

### Fixed

- **Filtering performance**: WordSiv uses more efficient regex matching and
  caching under the hood, greatly speeding up word filtering compared to the
  previous Python-level loops.
- **Default punctuation**: Language-specific punctuation is refined to reflect
  typical usage. Toggle it with `punc=True/False` and adjust distribution
  randomness via `rnd_punc`.

### Changed

- **Single `case` parameter**: Replaces multiple booleans (`uc`, `lc`, `cap`).
  Use `case="any"`, `"lc"`, `"uc"`, `"cap"`, etc. to control exactly which case
  you want and whether you're willing to modify original casing (gently or
  forcefully).
- **Shorter method names**:
    - `sentence` → `sent`
    - `sentences` → `sents`
    - `paragraph` → `para`
    - `paragraphs` → `paras`
- **`source` → `vocab`**: Instead of passing `source="..."`, specify
  `vocab="..."`.
    - See available Vocabs with `list_vocabs()`.
- **Seeding**: WordSiv no longer has an internal default seed.
    - Call `WordSiv(seed=123)` or `wsv.seed(123)` for deterministic results.
    - Most generation methods (e.g., `word()`, `words()`, `para()`, etc.) also
    accept a `seed` argument.
    - `top_word()` and `top_words()` do not use randomness, so `seed` is
    irrelevant there.
- **Parameter name changes**:
    - `prob=...` → `rnd=0..1`: controls how random vs. frequency-based word
    selection is (`rnd=0` = fully frequency-based, `rnd=1` = fully random).
    - `num_top=...` → `top_k=...`: if you need to limit to the top K words in
    frequency order on random picks, use `top_k`.

### Removed

- **Models and Source Packages** (`RandomModel`, `SequentialModel`,
  `MarkovModel`):
    - Models have been removed, and Source Packages are replaced by Vocabs,
      some of which are bundled with WordSiv itself. However:
        - **RandomModel** can be replicated `rnd=1`.
        - **SequentialModel** can be replicated with `top_word()` /
          `top_words()`.
        - **MarkovModel** has **no direct replacement**.
- **Font-based glyph inspection** and **bounding-box width filtering**:
    - These relied on `fonttools` and introduced extra complexity. Inspecting
      fonts is now up to the user.
