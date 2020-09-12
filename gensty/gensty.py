#!/usr/bin/env python
"""gensty - Latex package generator ttf/otf and SMuFL."""
import os
import sys
import argparse
from . import helpers
from datetime import datetime

__author__ = 'Georgios Tsotsos'
__email__ = 'tsotsos@gmail.com'
__version__ = '0.2.5'



def _singleFontData(font, version, forcedName):
    """Creates dict for single font to append into fonts dict on setupVariables
    hodling data for all fonts."""
    name = _fontName(font)
    defcmd, cmd = _latexDefCommands(name, forcedName)
    return {
        'fontname': name,
        'fontnameN': _fontNameIdentifier(name),
        'fontpath': font,
        'fontbase': os.path.basename(font),
        'description': _latexDescription(name, version),
        'definition': defcmd,
        'command': cmd
    }


def setupVariables(fontpath, version, author, forcedName):
    """ Produces usable data for  font(s) and validates arguments. Used to
    create the final Style package."""

    # optional arguments.
    version, author = _optionalArguments(version, author)

    path = _isFontPath(fontpath)
    fonts = _getFontsByType(fontpath)

    if not isinstance(fonts, list):
        raise Exception("Error could not retrieve fonts.")
    # font specific data.
    fontnames = {}
    for font in fonts:
        fontnames[_fontName(font)] = _singleFontData(font, version, forcedName)

    if len(fontnames) == 0:
        raise Exception("Error could not retrieve fonts.")

    return {
        'isfile': path,
        'year': datetime.today().strftime('%Y'),
        'author': author,
        'version': version,
        'fontnames': fontnames,
        'totalFonts': len(fonts),
    }


def retrieveCodes(filepath, smufl):
    """Retrieves the codepoints and symbols for the desired font, handles
    differently if its smufl font."""
    if smufl != None and _checkExtension(smufl, "json") == False:
        raise Exception("Error! Please provide a valid smufl json file")
    elif smufl != None and _checkExtension(smufl, "json") == True:
        return _glyphnameParse(smufl)
    else:
        charcodes = _fontCodepoints(filepath)
        charcodes = _fontCharList(charcodes, excluded=["????", "Space"])
        if isinstance(charcodes, list):
            return charcodes
        else:
            raise Exception("Uknown font parse error")


def _singlePackage(fontpath, fontname, content):
    """Creates a single package folder and its files."""
    _createDir(fontname)
    packageFontsPath = fontname + "/fonts"
    _createDir(packageFontsPath)
    shutil.copy2(fontpath, packageFontsPath)
    _writePackage(fontname+"/"+fontname, content)


def savePackage(fontPackages):
    """Creates the final package with style and font files. Based on fontPackage
    dict makePackage() produces."""

    if not bool(fontPackages):
        raise Exception("Error, could not create font package(s).")
    import pprint
    if fontPackages["packageName"] != None:
        packageName = fontPackages["packageName"]
        packageFontsPath = packageName + "/fonts"
        _createDir(packageName)
        _createDir(packageFontsPath)
        _writePackage(packageName+"/"+packageName, fontPackages["files"][0])
        for font in fontPackages["fontfiles"]:
            shutil.copy2(font, packageFontsPath)
    else:
        for idx, fontfile in enumerate(fontPackages["fontfiles"]):
            _singlePackage(fontfile,
                           fontPackages["fontnames"][idx],
                           fontPackages["files"][idx])


def makePackage(fontpath, version=None, author=None, smufl=None, packageName=None, forcedName=None):
    """After setupVariables() we can safely use them to create Style
    pacakage(s)."""
    data = setupVariables(fontpath, version, author, forcedName)
    fontData = data["fontnames"]
    result = {}
    styfiles = []
    fontnames = []
    fontpaths = []
    if packageName != None and packageName != "":
        header = _latexHeaderPartial(
            data["year"], data["author"], data["version"], packageName)
        defcmds = ""
        commands = ""
        for val in fontData:
            fontpaths.append(fontData[val]["fontpath"])
            fontnames.append(val)
            defcmds += _latexDefCommandsPartial(fontData[val])
            commands += _latexCommands(fontData[val]
                                       ["fontpath"], smufl, forcedName)
        styfiles.append(header + defcmds + commands)
    else:
        for val in fontData:
            fontpaths.append(fontData[val]["fontpath"])
            fontnames.append(val)
            header = _latexHeaderPartial(
                data["year"], data["version"], data["author"], val)
            defcmds = _latexDefCommandsPartial(fontData[val])
            commands = _latexCommands(
                fontData[val]["fontpath"], smufl, forcedName)
            styfiles.append(header + defcmds + commands)

    result = {
        'packageName': packageName,
        'fontsNumber': len(fontpaths),
        'fontnames': fontnames,
        'fontfiles': fontpaths,
        'files': styfiles,
    }
    return result


def main():
    parser = argparse.ArgumentParser(
        prog='genSty', description="LaTeX Style file generator for fonts")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('path',
                        help='Font(s) path. It can be either a directory in case of multiple fonts or file path.')
    parser.add_argument('--all', '-a', action="store_true",
                        help='If choosed %(prog)s will generate LaTeX Styles for all fonts in directory')
    parser.add_argument('--smufl', '-s', type=str,
                        help='If choosed %(prog)s will generate LaTeX Styles for all fonts in directory based on glyphnames provided.')
    parser.add_argument('--one-package', type=str,
                        help='Creates one package with name provided by this argument.')
    parser.add_argument('--force-name', type=str,
                        help='Forces LaTeX command name. Use with cautious in case of simmilar symbols on same package there will be an error.')
    parser.add_argument('--author', type=str, help='Author\'s name.')
    parser.add_argument('--ver', type=str, help='LaTeX package version.')
    args = parser.parse_args()

    # Handles different cases of command.
    # In case of "all" flag we create styles for every font in folder. For both
    # "all" true/false createPackage creates the the LaTeX style content and
    # package.
    if args.all == True and os.path.isdir(args.path) == False:
        raise Exception(
            "Error! flag --all must be defined along with directory only!")

    if args.smufl != None and _checkExtension(args.smufl, "json") == False:
        raise Exception("Error! Please provide a valid smufl json file")

    fontPackages = makePackage(
        args.path, args.ver, args.author, args.smufl, args.one_package, args.force_name)
    # creates font package with folder stracture etc.
    savePackage(fontPackages)


if __name__ == "__main__":
    main()
