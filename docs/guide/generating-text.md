# Generating Text

## Most Probable Words

Sometimes we want to see common words which we can spell with `glyphs`, without
any probability or randomization—especially when we have restrictive filters.
You can use `top_word` and `top_words` for this:

```python
--8<-- "top-words.py"
```

These functions are especially useful in seeing how WordSiv's
[filter arguments](filtering-words.md) work.
