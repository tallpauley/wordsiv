# Basic Usage

## Importing and initializing WordSiv

Once you've [installed](../index.md#installation) WordSiv, try generating a
sentence:
```python
--8<-- "import.py"
```

You should see a random sentence in the console in the lower-right of DrawBot!

## Listing Vocabs

WordSiv generates text using [Vocabs](../../api-reference/#wordsiv.Vocab):
objects that contain a word list (usually with counts) for a given language.
WordSiv includes some Vocabs, and you can make your own (instructions coming
soon!). See all available vocabs with: `list_vocabs()`:

```python
--8<-- "list-vocabs.py"
```

## Selecting a Vocab

You can set the default Vocab on `WordSiv` object initialization:
```python
--8<-- "default-vocab.py"
```

Or specify `vocab` when you are calling `word()`, `sent()`, etc.:
```python
--8<-- "vocab-arg.py"
```

!!! Note
    The `vocab` argument for `word()`, `sent()`, etc. has precedence:
    ```python
    --8<-- "set-vocab-arg-precedence.py"
    ```

## Restricting the Glyph Set

You can set the default glyphs on `WordSiv` object initialization:
```python
--8<-- "set-glyphs.py"
```

Or specify `glyphs` when you are calling `word()`, `sent()`, etc.:
```python
--8<-- "glyphs-arg.py"
```

!!! Note
    The `glyphs` argument for `word()`, `sent()`, etc. has precedence:
    ```python
    --8<-- "set-glyphs-arg-precedence.py"
    ```
