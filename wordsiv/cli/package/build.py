from typing import Optional
from pathlib import Path

SETUP_PY_TEMPLATE = """
#!/usr/bin/env python3
# coding: utf8

import json
from os import path, walk
from shutil import copy
from setuptools import setup

def load_meta(fp):
    with open(fp, encoding='utf8') as f:
        return json.load(f)


def list_files(data_dir):
    output = []
    for root, _, filenames in walk(data_dir):
        for filename in filenames:
            if not filename.startswith('.'):
                output.append(path.join(root, filename))
    output = [path.relpath(p, path.dirname(data_dir)) for p in output]
    output.append('meta.json')
    return output


def list_requirements(meta):
    requirements = ['wordsiv' + meta['wordsiv_version']]
    if 'setup_requires' in meta:
        requirements += meta['setup_requires']
    return requirements


def setup_package():
    root = path.abspath(path.dirname(__file__))
    meta_path = path.join(root, 'meta.json')
    print(meta_path)
    meta = load_meta(meta_path)
    package_name = meta['name']
    data_source_dir = path.join(package_name, 'data')

    copy(meta_path, path.join(package_name))
    copy(meta_path, data_source_dir)

    setup(
        name=package_name,
        description=meta['description'],
        author=meta['author'],
        author_email=meta['email'],
        url=meta['url'],
        version=meta['version'],
        license=meta['license'],
        packages=[package_name],
        package_data={package_name: list_files(data_source_dir)},
        install_requires=list_requirements(meta),
        zip_safe=False,
        entry_points= {
            'wordsiv_source_modules': [
                '{p} = {p}'.format(p=package_name)
            ]
        }
    )

if __name__ == '__main__':
    setup_package()
""".strip()

MANIFEST_TEMPLATE = """
include meta.json
include LICENSE
""".strip()


def build_package(source_dir: Optional[Path], output_dir: Optional[Path]):
    """Package a wordsiv Source module as wheel & sdist
    
    See https://github.com/tallpauley/wordsiv-source-packages for examples of what
    SOURCE_DIR should look like.
    """

    temp_dir = Path.cwd() / ".wordsiv-temp"

    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.copytree(source_dir, temp_dir)

    with open(temp_dir / "manifest.in", "w+") as f:
        f.write(MANIFEST_TEMPLATE)

    with open(temp_dir / "setup.py", "w+") as f:
        f.write(SETUP_PY_TEMPLATE)

    pb = build.ProjectBuilder(temp_dir)
    pb.build("wheel", output_dir)
    pb.build("sdist", output_dir)

    shutil.rmtree(temp_dir, ignore_errors=True)
