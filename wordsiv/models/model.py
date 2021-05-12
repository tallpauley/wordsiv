from abc import ABC, abstractmethod

#####################################################################################
###### TEXT MODELS
#####################################################################################


class TextModel(ABC):
    """TextModel is a base class which only implements sentences() and larger"""

    @classmethod
    @abstractmethod
    def create_and_run(
        cls, method, data_wrap, available_glyphs, font_info, rand, **kwargs
    ):
        """Create model, and run method

        Allows model to define what kwargs are needed for model initialization and which
        kwargs are fed to the runtime method (word(), sentence(), text(), etc())
        """
        raise NotImplementedError

    @abstractmethod
    def word(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError

    @abstractmethod
    def words(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError

    @abstractmethod
    def sentence(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError

    def sentences(self, num_sents=5, **kwargs):
        """Return a list of sentence strings"""

        return [self.sentence(**kwargs) for _ in range(num_sents)]

    def paragraph(self, **kwargs):
        """Return a paragraph string"""

        return " ".join(self.sentences(**kwargs))

    def paragraphs(self, num_paras=3, **kwargs):
        """Return an iterable of paragraph strings"""

        return [self.paragraph(**kwargs) for _ in range(num_paras)]

    def text(self, **kwargs):
        """Return a string of a block of text"""

        return "\n\n".join(self.paragraphs(**kwargs))


class WordTextModel(TextModel):
    """A Text Model which generates simple text with a WordModel

    It caches each word model for performance
    """

    @classmethod
    def create_and_run(
        cls, method, data_wrap, available_glyphs, font_info, rand, **kwargs
    ):
        """Creates model, sending all **kwargs to the method being called"""

        model = cls(data_wrap, available_glyphs, font_info, rand)
        return getattr(model, method)(**kwargs)

    def __init__(self, data_wrap, available_glyphs, font_info, rand):

        # No filtering on initialization since filtering happens at word level
        self.data_wrap = data_wrap
        self.available_glyphs = available_glyphs
        self.font_info = font_info
        self.rand = rand

    @abstractmethod
    def create_word_model(self, **kwargs):
        """Filter data and return a new WordModel

        No need to cache here, we let word model itself handle this"""

        raise NotImplementedError

    def word(self, **kwargs):
        """Return a single word string"""

        return self.create_word_model(**kwargs).word()

    def words(
        self, num_words=None, cap_first=False, uc=False, lc=False, cap=False, **kwargs
    ):
        """Return a list of word strings"""

        if not num_words:
            num_words = self.rand.randrange(10, 20)

        # TODO: test or error out when multiple conflicting options are set
        def cap_first(n):
            return cap or (cap_first and n == 0)

        return [
            self.word(cap=cap_first(n), uc=uc, lc=lc, **kwargs)
            for n in range(num_words)
        ]

    def sentence(
        self, cap_sent=True, sent_len=None, term=True, punc_func=None, **kwargs
    ):
        """Return a sentence string"""

        # TODO: Revisit how to get default punc func from source
        # Also, we can have more advanced punctuation options in TemplateTextModel
        # TODO: And EVENTUALLY TemplateTextModel could implement
        # E.G. for WordTextModel: We could supply template:
        # def template(mayb, pword, r):
        #    return mayb(sp) + pword(cap=True), pword() * r(7,15), mayb(ep)
        if not punc_func:

            def punc_func(x):
                return x

        sent = " ".join(self.words(num_words=sent_len, cap_first=cap_sent, **kwargs))

        return punc_func(sent)


#####################################################################################
###### WORD MODELS
#####################################################################################


class WordModel(ABC):
    """A WordModel is a model for generating single words at a time

    They aren't intended to be directly accessed via a Wordsiv object. Rather they are a
    compositional object which can be plugged into models like WordTextModel.
    """

    @abstractmethod
    def word(self):
        """Return a single word string"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create(self, data_wrap, rand):
        """Given a DataWrapper, create a WordModel.

        We use this as main interface to allow caching"""
        raise NotImplementedError


class CachedWordModel(WordModel):
    """A WordModel that caches models based on their input data"""

    _instances = {}  # type: ignore

    @classmethod
    def create(cls, data_wrap, rand):
        """Factory method to initialize object if data is unique, or use cached one"""

        # Objects are cached using hash from data_wrap
        if data_wrap in cls._instances:
            return cls._instances[data_wrap]
        else:
            instance = cls(data_wrap, rand)
            cls._instances[data_wrap] = instance
            return instance
