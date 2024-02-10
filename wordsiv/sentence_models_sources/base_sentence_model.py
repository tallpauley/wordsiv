from abc import ABC, abstractmethod

#####################################################################################
###### BASE TEXT MODELS
#####################################################################################


class BaseSentenceModel(ABC):
    """BaseSentenceModel is the abstract base class for all Sentence Models"""

    @classmethod
    @abstractmethod
    def create_model(cls, data, available_glyphs, rand, language, **kwargs):
        """Create model, and return (model, **kwargs)

        Allows model to define what kwargs are needed for model initialization and which
        kwargs are returned for the runtime method (word(), sentence(), text(), etc())
        """
        raise NotImplementedError

    def word(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError(f"word() is not defined for {type(self).__name__}")

    def words(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError(f"words() is not defined for {type(self).__name__}")

    def sentence(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError(
            f"sentence() is not defined for {type(self).__name__}"
        )
