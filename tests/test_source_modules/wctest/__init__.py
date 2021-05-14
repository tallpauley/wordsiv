from wordsiv.text_models_sources import WordCountSource, ProbabilityModel, RandomModel

from pathlib import Path
import json

# Assuming installed as directory (zip_safe=False)
HERE = Path(__file__).parent.absolute()

# Sources should always be prefixed with the package name
# as they will be merged into a common namespace
sources = {
    "wctest": WordCountSource(HERE / "data" / "count-source.txt"),
    "wctest_sm": WordCountSource(HERE / "data" / "count-source.txt", 10),
}

# dictionary of "pipelines": preset maps of sources to models
# Pipelines should also be prefixed with the package name
pipelines = {
    "wctest": {
        "source": sources["wctest"],
        "model_class": ProbabilityModel,
    },
    "wctest_rand": {
        "source": sources["wctest"],
        "model_class": RandomModel,
    },
}
