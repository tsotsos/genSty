
# genSty

![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/tsotsos/gensty?include_prereleases) ![PyPI - Status](https://img.shields.io/pypi/status/gensty) [![PyPI version](https://badge.fury.io/py/gensty.svg)](https://badge.fury.io/py/gensty) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gensty) [![License](https://img.shields.io/github/license/tsotsos/gensty.svg)](https://github.com/tsotsos/gensty)

GenSty is a LaTex style package generator for OpenType fonts (otf/ttf) which
supports W3C SMuFL notation. With gensty you can generate your LaTeX package
based on any OpenType font; the generator parses ttf/otf files and creates LaTeX
commands for all Unicode Symbols. In the case of SMuFL fonts, you can also include
the glyphnames.json file, so it will create friendlier names and include
"Private Use" symbols.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```console
pip install gensty
```

## Installation (manual)

Clone the repository

```console
git clone git@github.com:tsotsos/genSty.git
```

and then use from the top folder. Eg.

```console
python3 -m gensty -h
```

## Usage

As referred above, the package can be used directly, installed from pip, and as
a module. In case of command line the script can be used :

```console
gensty -h

usage: genSty [-h] [--version] [--all] [--smufl SMUFL]
              [--one-package ONE_PACKAGE] [--author AUTHOR] [--ver VER]
              path

LaTeX Style file generator for fonts

positional arguments:
  path                  Font(s) path. It can be either a directory in case of
                        multiple fonts or file path.

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --all, -a             If choosed genSty will generate LaTeX Styles for all
                        fonts in directory
  --smufl SMUFL, -s SMUFL
                        If choosed genSty will generate LaTeX Styles for all
                        fonts in directory based on glyphnames provided.
  --one-package ONE_PACKAGE
                        Creates one package with name provided by this
                        argument.
  --author AUTHOR       Author's name.
  --ver VER             LaTeX package version.
```

### Use as a module

Use the module to create LaTeXstyle instances and handle generated latex code 
yourself.

```python
import gensty

# Generate LaTeXstyle instance from font file:

latexObj = font.LaTeXstyle(author,version, "path/to/font.otf",smufl)

# then you can get for latexObj,Header(), DefCommands(), Commands() or File()
```

Use them module to create the LaTeX package in filesystem.

```python
import gensty

# Use the same functions as gensty CLI and handle both folder or font file
# input (path can be either font file or folder including fonts).
# Then using savePackage you can save the generated output to disk
# accorndingly.
# smufl is the path to glyphnames.json which is defined according to W3C
# Specifications https://www.w3.org/2019/03/smufl13/specification/glyphnames.html

# prepare fonts. author, version and smuf, can be None.
fonts = prepareFonts(path, version, author, smufl)

# packageName and forcedCommand can be None. They are used to force LaTeX
# pacakage name and commands respectively.
fontnames, fontfiles, files = makePackage(fonts, packageName, forcedCommand)

# creates font package in file system.
savePackage(fontnames, fontfiles, files, packageName)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

