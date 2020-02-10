#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# setup.py
#

import io
import json
import os
import sys
import hashlib
from shutil import rmtree
from setuptools import setup, find_packages, Command


SETUP_JSON = "setup.json"


HERE = os.path.abspath(os.path.dirname(__file__))


def load_json(path, here=HERE):
    """Load Setup.Json."""
    with io.open(os.path.join(here, path)) as f:
        return json.load(f)


def get_long_description(path, default="", here=HERE):
    """Get Long Description from README."""
    long_description = default
    with io.open(os.path.join(here, path), encoding="utf-8") as f:
        long_description = "\n" + f.read()
    return long_description


def get_version(path, key="__version__", here=HERE):
    """Get Version from Version File."""
    version = {}
    with open(os.path.join(here, path)) as f:
        exec(f.read(), version)
    return version[key]


def print_bold(string):
    """Print Bold String."""
    print(f"\033[1m{string}\033[0m")


def setup_yaml(path, target, **kwargs):
    """Setup Meta Yaml."""
    with open(target, "w") as target_file:
        with open(path, "r") as source_file:
            for line in source_file:
                try:
                    target_file.write(line.format(**kwargs))
                except KeyError:
                    target_file.write(line)


def compute_package_hash(self):
    """"""


class CondaBuild(Command):
    """
    Conda Build Command.

    """


class Upload(Command):
    """
    Upload Command.

    """

    name = "upload"
    description = "Build and publish the package."
    user_options = []

    def initialize_options(self):
        """Initialize Options."""

    def finalize_options(self):
        """Finalize Options."""

    def run(self):
        """Run Upload."""
        try:
            print_bold("Removing previous builds ...")
            rmtree(os.path.join(HERE, "dist"))
        except OSError:
            pass
        print_bold("Building Source and Wheel (universal) distribution...")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")
        print_bold("Uploading the package to PyPI via Twine...")
        os.system(
            "twine upload --repository-url https://upload.pypi.org/legacy/ dist/*"
        )
        sys.exit()


if __name__ == "__main__":
    about = load_json(SETUP_JSON)

    about["version"] = get_version(about["version_file"])
    del about["version_file"]

    about["long_description"] = get_long_description(about["long_description_file"])
    del about["long_description_file"]

    if "exclude" in about["packages"]:
        about["packages"] = find_packages(exclude=tuple(about["packages"]["exclude"]))

    try:
        conda_build_file = about["conda_build_file"]
        del about["conda_build_file"]
    except KeyError:
        pass

    setup(cmdclass={Upload.name: Upload}, **about)
