
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

and then use via gensty/gensty folder. Eg.

```bash
python3 /the/path/of/gensty/gensty.py
```

## Usage

As referred above, the package can be used directly, installed from pip, and as
a module. In case of command line the script can be used :

```console
usage: genSty [-h] [--version] [--all] [--smufl SMUFL]
                    [--description DESCRIPTION] [--author AUTHOR] [--ver VER]
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
  --description DESCRIPTION
                        LaTeX Style package description. It is ignored in case
                        of --all flag.
  --author AUTHOR       Author's name.
  --ver VER             LaTeX package version.
```

### Use as a module

```python
import gensty

# To create all style packages from a folder or fontfile (path). use
# makePackage().
# Optional arguments: version, author and smufl.
# smufl is path to glyphnames.json which is defined according to Specifications
# https://www.w3.org/2019/03/smufl13/specification/glyphnames.html

fontpaths, files = gensty.makePackage(path, version, author, smufl)

# if you want to save style packages in a folder use:
savePackage(fontpaths,files)

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

