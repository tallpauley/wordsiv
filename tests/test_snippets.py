import pytest
from pathlib import Path
import subprocess

# Directory containing the snippet files
SNIPPETS_DIR = Path("docs/snippets")


def get_snippet_files():
    """Retrieve a list of all files in the snippets directory."""
    return [f for f in SNIPPETS_DIR.iterdir() if f.is_file()]


@pytest.mark.parametrize("snippet_file", get_snippet_files())
def test_snippet(snippet_file):
    """Run each snippet file as a test."""
    # Assuming the snippets are Python scripts, you can execute them using subprocess
    result = subprocess.run(
        ["python", str(snippet_file)], capture_output=True, text=True
    )

    # Check if the script ran successfully
    assert (
        result.returncode == 0
    ), f"Snippet {snippet_file} failed with error: {result.stderr}"
