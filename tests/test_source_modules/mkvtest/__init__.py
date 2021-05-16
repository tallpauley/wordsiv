from wordsiv.sentence_models_sources import MarkovSource, MarkovModel

from pathlib import Path
import json

# Assuming installed as directory (zip_safe=False)
HERE = Path(__file__).parent.absolute()

# Sources should always be prefixed with the package name
# as they will be merged into a common namespace
sources = {"mkvtest": MarkovSource(HERE / "data" / "markov-source.json")}

# dictionary of "pipelines": preset maps of sources to models
# Pipelines should also be prefixed with the package name
pipelines = {
    "mkvtest": {
        "source": sources["mkvtest"],
        "model_class": MarkovModel,
    }
}
