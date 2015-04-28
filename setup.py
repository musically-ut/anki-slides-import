from setuptools import setup
import sys

# The argparse module was introduced in python 2.7 or python 3.2
REQUIRES = ["argparse"] if sys.version[:3] in ('2.6', '3.0', '3.1') else []
REQUIRES = REQUIRES + ["wand>=0.4.0"]

setup(
    version='0.0.1',
    name="anki-slides-import",
    author="Utkarsh Upadhyay",
    author_email="musically.ut@gmail.com",
    description = "Convert text notes and slides into an Anki deck.",
    license="MIT",
    keywords="anki slides deck import",
    install_requires=REQUIRES,
    url="https://github.com/musically-ut/anki-slides-import",
    packages=["slidesimport"],
    entry_points={ "console_scripts": [ "slides2anki = slidesimport.slidesimport:run" ]},
    classifiers      = [
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Natural Language :: English"
    ],
)
