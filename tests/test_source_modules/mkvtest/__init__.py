from wordsiv.sentence_models_sources import MarkovSource, MarkovModel

from pathlib import Path
import json

# Assuming installed as directory (zip_safe=False)
HERE = Path(__file__).parent.absolute()

with open(HERE / "meta.json", "r") as f:
    meta = json.load(f)

# Sources should always be prefixed with the package name
# as they will be merged into a common namespace
sources = {
    "mkvtest": {
        "source": MarkovSource(HERE / "data" / "markov-source.json", meta),
        "default_model_class": MarkovModel,
    },
}
