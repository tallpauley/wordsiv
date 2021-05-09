import typer

from . import build
from . import list as list_packages

app = typer.Typer()

app.command("list")(list_packages.list_packages)
app.command("build")(build.build_package)
