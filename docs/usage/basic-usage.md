# Basic Usage

## Importing and initializing WordSiv

Once you've [installed](../index.md#installation) WordSiv, try generating a
sentence:
```python
--8<-- "import.py"
```

You should see a random sentence in the console in the lower-right of DrawBot!

Check out the [Quick Reference](../examples/quick-reference.md) if you want to
quickly jump into WordSiv, or read on for more detailed information.

## Listing Vocabs

WordSiv generates text using [Vocabs](../api-reference.md#wordsiv.Vocab):
objects that contain a word list (usually with occurrence counts) for a given
language. WordSiv includes some Vocabs, and you can make your own (instructions
coming soon!). You can see all available Vocabs with: `list_vocabs()`:

```python
--8<-- "list-vocabs.py"
```

## Selecting a Vocab

You can set which Vocab you want to use on `WordSiv` object initialization,
which will affect all text generation methods you call:
```python
--8<-- "default-vocab.py"
```

Alternatively, you can specify `vocab` when you are calling `word()`, `sent()`,
etc.:
```python
--8<-- "vocab-arg.py"
```

!!! Note
    The `vocab` argument for `word()`, `sent()`, etc. has precedence:
    ```python
    --8<-- "set-vocab-arg-precedence.py"
    ```

## Restricting the Glyph Set

The `glyphs` argument specifies a whitelist of glyphs that WordSiv will use to
constrain text generation.

You can set `glyphs` on `WordSiv` object initialization, which will affect all
subsequent text generation methods you call:
```python
--8<-- "set-glyphs.py"
```

Alternatively, you can specify `glyphs` when you are calling `word()`, `sent()`,
etc.:
```python
--8<-- "glyphs-arg.py"
```

!!! Note
    The `glyphs` argument for `word()`, `sent()`, etc. has precedence:
    ```python
    --8<-- "set-glyphs-arg-precedence.py"
    ```
