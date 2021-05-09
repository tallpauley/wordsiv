import typer
from pathlib import Path
import shutil
import os
from os.path import basename
import build

from ..about import __version__
from ..utilities import installed_source_modules
from . import package

app = typer.Typer()
app.add_typer(package.app, name="package")


@app.command()
def download(data_package: str):
    print(data_package)


@app.command()
def info():
    print("Wordsiv Version: " + __version__)
