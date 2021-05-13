#!/usr/bin/env bash -e

# temporarily set this to false so we can make a new virtualenv
python -m venv ${PWD}/.venv_byexample
. .venv_byexample/bin/activate
pip install byexample
byexample -l shell,python README.md -o "+term=ansi"
rm -r .venv_byexample