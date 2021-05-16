from wordsiv.sentence_models_sources import WordCountSource, RandomModel

from pathlib import Path
import json

# Assuming installed as directory (zip_safe=False)
HERE = Path(__file__).parent.absolute()

with open(HERE / "meta.json", "r") as f:
    meta = json.load(f)

# Sources should always be prefixed with the package name
# as they will be merged into a common namespace
sources = {
    "wctest": {
        "source": WordCountSource(HERE / "data" / "count-source.txt", meta),
        "default_model_class": RandomModel,
    },
    "wctest_sm": {
        "source": WordCountSource(HERE / "data" / "count-source.txt", meta, 10),
        "default_model_class": RandomModel,
    },
}
