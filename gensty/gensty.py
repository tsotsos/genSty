#!/usr/bin/env python
"""gensty - Latex package generator ttf/otf and SMuFL."""
import os
import json
import sys
import shutil
import argparse
from datetime import datetime
from fontTools import ttLib
from fontTools.unicode import Unicode

__author__ = 'Georgios Tsotsos'
__email__ = 'tsotsos@gmail.com'
__version__ = '0.2.4'
__supported_fonts__ = ['ttf', 'otf']
__header_template = 'resources/header.sty'
__commands_template = 'resources/defcommands.sty'


def _isFontPath(path):
    """ Checks if the path is file or folder. In case of folder returns all
    included fonts."""
    if os.path.isfile(path):
        return True
    elif os.path.isdir(path):
        return False
    else:
        raise Exception("Error. Path must be a valid file or folder.")


def _findByExt(path, ext):
    """Finds file by extension. Returns list."""
    files = []
    if os.path.isfile(path) == True:
        if _checkExtension(path, ext) == True:
            files.append(path)
        else:
            return False
    else:
        for file in os.listdir(path):
            if file.endswith("."+ext):
                files.append(os.path.join(path, file))
    return files


def _createDir(dir):
    """Forces directory creation by removing any pre-existing folder with same
    name."""
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def _checkExtension(path, ext):
    """Defines if a file exists and its json."""
    if not os.path.isfile(path):
        return False
    if not path.endswith("."+ext):
        return False
    return True


def _writePackage(fontname, code):
    """Writes Style file."""
    sty = open(fontname+".sty", "w")
    sty.write(code)
    sty.close()


def _glyphnameParse(glyphnameFile):
    """Parses glyphname file according w3c/smufl reference."""
    result = []
    with open(glyphnameFile) as json_file:
        gnames = json.load(json_file)
        for gname in gnames:
            codepoint = gnames[gname]["codepoint"].replace("U+", "")
            result.append((int(codepoint, 16), gname))
    return result


def _ReplaceToken(dict_replace, target):
    """Based on dict, replaces key with the value on the target."""

    for check, replacer in list(dict_replace.items()):
        target = target.replace("["+check+"]", replacer)

    return target


def _getFontsByType(path):
    """Gets supported fonts by file extesion in a given folder."""
    files = []
    for ext in __supported_fonts__:
        fonts = _findByExt(path, ext)
        if not isinstance(fonts, list):
            continue
        for font in fonts:
            files.append(font)

    return files


def _fontName(fontfile):
    """Get the name from the font's names table.
    Customized function, original retrieved from: https://bit.ly/3lS4nMO
    """
    name = ""
    font = ttLib.TTFont(fontfile)
    for record in font['name'].names:
        if record.nameID == 4 and not name:
            if b'\000' in record.string:
                name = str(record.string, 'utf-16-be').encode('utf-8')
            else:
                name = record.string
                if name:
                    break
    font.close()
    # TODO: test for issues with multiple fonts
    name = name.decode('utf-8')
    return name.replace(" ", "").replace("-", "")


def _fontNameIdentifier(fontname, prefix=True):
    """Removes spaces and forces lowercase for font name, by default adds prefix
    'fnt' so we can avoid issues with simmilar names in other LaTeX packages."""
    result = fontname.lower().replace(" ", "")
    if prefix == True:
        return "fnt"+result
    return result


def _fontCodepoints(fontfile):
    """Creates a dict of codepoints and names for every character/symbol in the
    given font."""
    font = ttLib.TTFont(fontfile)
    charcodes = []
    for x in font["cmap"].tables:
        if not x.isUnicode():
            continue
        for y in x.cmap.items():
            charcodes.append(y)
    font.close()
    sorted(charcodes)
    return charcodes


def _fontCharList(charcodes, private=False, excluded=[]):
    """Accepts list of tuples with charcodes and codepoints and returns
    names and charcodes."""
    if not isinstance(charcodes, list):
        return False
    result = []
    for charcode, codepoint in charcodes:
        description = _latexFriendlyName(Unicode[charcode])
        if private == True and charcode >= 0xE000 and charcode <= 0xF8FF:
            continue
        if description in excluded:
            continue
        result.append((charcode, description))
    return result


def _latexFriendlyName(s):
    """Oneliner to return normalized name for LaTeX Style package."""
    return(" ".join(x.capitalize() for x in s.split(" ")).replace(" ", "").replace("-", ""))


def _latexDescription(fontname, version):
    """Creates default description text based on name and version."""
    currentDate = datetime.today().strftime('%Y-%m-%d')
    return "%s %s LaTeX package for %s" % (currentDate, version, fontname)


def _latexRequirements(requirements):
    """Creates LaTeX package requirements. By default fontspec is nessessary."""
    reqstr = "\\RequirePackage{fontspec}"
    if not isinstance(requirements, list):
        return reqstr
    for pkg in requirements:
        if pkg == "fontspec":
            continue
        reqstr += "\\RequirePackage{"+pkg+"}"
    return reqstr


def _latexDefCommands(fontname, forced=None):
    """Creates command name, definition and command."""

    if forced != None:
        defCmd = "Define"+forced
        return (defCmd, forced)

    defCmd = "Define"+fontname
    return (defCmd, fontname)


def _latexCommands(fontfile, smufl, forcedName):
    """Generates LaTeX commands for each char code."""
    charcodes = retrieveCodes(fontfile, smufl)
    if not isinstance(charcodes, list):
        return False
    fontname = _fontName(fontfile)
    cmds = _latexDefCommands(fontname, forcedName)
    commands = "\n"
    for codepoint, desc in charcodes:
        commands += "\\"+cmds[0]+"{"+desc+"}{\\symbol{"+str(codepoint)+"}}\n"
    if commands == "\n":
        raise Exception("Error. Cannot create LaTeX style commands")
    return commands


def _latexHeaderPartial(year, author, version, packageName):
    """Fills header style partial."""
    tokens = {
        'packageName': packageName,
        'description': _latexDescription(packageName, version),
        'year': year,
        'author': author,
    }
    return _makeTemplate("header.sty", tokens)


def _latexDefCommandsPartial(fontData):
    """Fills Commands definition style partial."""
    tokens = {
        'fontfile': fontData["fontbase"],
        'fontspath': "fonts",
        'fontfamily': fontData["fontnameN"],
        'fntidentifier': fontData["fontnameN"],
        'defcommand': fontData["definition"],
        'command': fontData["command"],
    }
    return _makeTemplate("defcommands.sty", tokens)


def _makeTemplate(template, tokens):
    """Parses and replace tokens in template string."""
    genstyPath = os.path.abspath(os.path.dirname(__file__))
    with open(genstyPath+"/resources/"+template) as templateFile:
        template = templateFile.read()
        output = _ReplaceToken(tokens, template)
    return output


def _optionalArguments(version, author):
    """Validates and ensure existance of optional arguments."""
    if version == None:
        version = "v.0.1"
    if author == None:
        author = __author__

    return version, author


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

    fontPackages = makePackage(
        args.path, args.ver, args.author, args.smufl, args.one_package, args.force_name)
    # creates font package with folder stracture etc.
    savePackage(fontPackages)


if __name__ == "__main__":
    main()
