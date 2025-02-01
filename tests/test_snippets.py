import pytest
from pathlib import Path
import subprocess
import os

# Directory containing the snippet files
SNIPPETS_DIR = Path("docs/snippets")


def get_snippet_files():
    """Retrieve a list of all files in the snippets directory."""
    return [f for f in SNIPPETS_DIR.iterdir() if f.is_file() and f.suffix == ".py"]


@pytest.mark.parametrize("snippet_file", get_snippet_files())
def test_snippet(snippet_file):
    """Run each snippet file as a test."""
    cwd = os.path.dirname(os.path.realpath(snippet_file))
    filename = os.path.basename(snippet_file)
    result = subprocess.run(
        ["python", filename], capture_output=True, text=True, cwd=cwd
    )

    # Check if the script ran successfully
    assert (
        result.returncode == 0
    ), f"Snippet {snippet_file} failed with error: {result.stderr}"
