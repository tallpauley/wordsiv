"""WordSiv is a Python library for generating proofing text with a limited character set."""

from importlib_metadata import entry_points


class ModelNotFoundError(Exception):
    pass


class MultipleModelsFoundError(Exception):
    pass


class ModelDuplicateError(Exception):
    pass


class SourceDuplicateError(Exception):
    pass


class ModelEntry:
    def __init__(self, namespace, model_name, model):
        self.namespace = namespace
        self.model_name = model_name
        self.full_name = f"{namespace}.{model_name}"
        self.model = model


class SourceEntry:
    def __init__(self, namespace, source_name, source):
        self.namespace = namespace
        self.source_name = source_name
        self.full_name = f"{namespace}.{source_name}"
        self.source = source


class WordSiv:
    def __init__(self, glyphs: str = None, model: str = None, load_langpacks=True):
        self.default_glyphs = glyphs
        self.default_model = model

        self.source_entries = []
        self.model_entries = []

        if load_langpacks:
            self.load_langpacks()

    def set_glyphs(self, default_glyphs):
        self.default_glyphs = default_glyphs

    def set_model(self, default_model):
        self.default_model = default_model

    def add_model(self, model_name, model, namespace="default"):
        if any(
            me
            for me in self.model_entries
            if me.model_name == model_name and me.namespace == namespace
        ):
            raise ModelDuplicateError(
                "Model name '{model_name}' already exists in namespace '{namespace}'"
            )

        self.model_entries.append(ModelEntry(namespace, model_name, model))

    def add_source(self, source_name, source, namespace="default"):
        if any(
            se
            for se in self.source_entries
            if se.source_name == source_name and se.namespace == namespace
        ):
            raise SourceDuplicateError(
                "Source name '{source_name}' already exists in namespace '{namespace}'"
            )

        self.source_entries.append(SourceEntry(namespace, source_name, source))

    def load_langpacks(self):
        for ep in entry_points(group="wordsiv.langpack"):
            langpack_module = ep.load()
            self.load_langpack(langpack_module)

    def load_langpack(self, langpack_module):
        # add sources if exist in langpack
        for source_name, source in langpack_module.sources.items():
            self.add_source(source_name, source, namespace=langpack_module.namespace)

        # add models if exist in langpack
        for model_name, model in langpack_module.models.items():
            self.add_model(model_name, model, namespace=langpack_module.namespace)

    def get_model(self, query: str):

        if not query and self.default_model:
            query = self.default_model

        results = [
            me
            for me in self.model_entries
            if me.full_name == query or me.model_name == query
        ]
        if not results:
            raise ModelNotFoundError(f"no model named'{query}'")
        if len(results) > 1:
            full_names = " or ".join([f"'{me.full_name}'" for me in results])
            raise MultipleModelsFoundError(
                f"models named '{query}' in multiple langpacks. Try {full_names}'"
            )

        return results[0].model

    def list_models(self):
        return [me.full_name for me in self.model_entries]

    def word(self, model: str = None, glyphs: str = None, **kwargs) -> str:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).word(glyphs=glyphs, **kwargs)

    def words(self, model: str = None, glyphs: str = None, **kwargs) -> list[str]:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).words(glyphs=glyphs, **kwargs)

    def sent(self, model: str = None, glyphs: str = None, **kwargs) -> str:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).sent(glyphs=glyphs, **kwargs)

    def sents(self, model: str = None, glyphs: str = None, **kwargs) -> list[str]:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).sents(glyphs=glyphs, **kwargs)

    def para(self, model: str = None, glyphs: str = None, **kwargs) -> str:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).para(glyphs=glyphs, **kwargs)

    def paras(self, model: str = None, glyphs: str = None, **kwargs) -> list[str]:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).paras(glyphs=glyphs, **kwargs)

    def text(self, model: str = None, glyphs: str = None, **kwargs) -> str:
        glyphs = self.default_glyphs if not glyphs else glyphs

        return self.get_model(model).text(glyphs=glyphs, **kwargs)


_wordsiv_instance = WordSiv()


def set_glyphs(default_glyphs):
    _wordsiv_instance.set_glyphs(default_glyphs)


def set_model(default_model):
    _wordsiv_instance.set_model(default_model)


# Top-level functions that reference the singleton
def word(model: str = None, glyphs: str = None, **kwargs) -> str:
    return _wordsiv_instance.word(model=model, glyphs=glyphs, **kwargs)


def words(model: str = None, glyphs: str = None, **kwargs) -> list[str]:
    return _wordsiv_instance.words(model=model, glyphs=glyphs, **kwargs)


def sent(model: str = None, glyphs: str = None, **kwargs) -> str:
    return _wordsiv_instance.sent(model=model, glyphs=glyphs, **kwargs)


def sents(model: str = None, glyphs: str = None, **kwargs) -> list[str]:
    return _wordsiv_instance.sents(model=model, glyphs=glyphs, **kwargs)


def para(model: str = None, glyphs: str = None, **kwargs) -> str:
    return _wordsiv_instance.para(model=model, glyphs=glyphs, **kwargs)


def paras(model: str = None, glyphs: str = None, **kwargs) -> list[str]:
    return _wordsiv_instance.paras(model=model, glyphs=glyphs, **kwargs)


def text(model: str = None, glyphs: str = None, **kwargs) -> str:
    return _wordsiv_instance.text(model=model, glyphs=glyphs, **kwargs)
