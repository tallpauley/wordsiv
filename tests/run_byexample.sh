#!/usr/bin/env bash -e

# temporarily set this to false so we can make a new virtualenv
poetry config virtualenvs.in-project false
poetry env remove python3 || true
poetry env use python3
poetry run pip install byexample
poetry run byexample -l shell,python README.md -o "+term=ansi"