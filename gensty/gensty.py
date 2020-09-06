#!/usr/bin/env python
"""gensty - Latex package generator ttf/otf and SMuFL."""
import os
import json
import argparse
import sys
import shutil
from datetime import datetime
from fontTools import ttLib
from fontTools.unicode import Unicode

__author__ = 'Georgios Tsotsos'
__email__ = 'tsotsos@gmail.com'
__version__ = '0.1'


def isfile(path):
    """ Detects if the given string is file."""
    if os.path.isfile(path):
        return True
    return False


def isdir(path):
    """ Detects if the given string is directory."""
    if os.path.isdir(path):
        return True
    return False


def findByExt(path, ext):
    """Finds file by extension. Returns list."""
    files = []
    for file in os.listdir(path):
        if file.endswith("."+ext):
            files.append(os.path.join(path, file))
    return files

def createDir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def checkJson(path):
    """Defines if a file exists and its json."""
    if not isfile(path):
        return False
    if not path.endswith(".json"):
        return False
    return True


def getFontsByType(path):
    """Gets supported fonts by file extesion in a given folder."""
    files = []
    fontExt = ["otf", "ttf"]
    for ext in fontExt:
        fonts = findByExt(path, ext)
        if not isinstance(fonts, list):
            continue
        for font in fonts:
            files.append(font)

    return files


def fontName(fontfile):
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
    return name.replace(" ", "")


def fontCodepoints(fontfile):
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


def latexFriendlyName(s):
    """Oneliner to return normalized name for LaTeX Style package."""
    return(" ".join(x.capitalize() for x in s.split(" ")).replace(" ", "").replace("-", ""))


def fontNormalize(charcodes, private=False, excluded=[]):
    """Accepts list of tuples with charcodes and codepoints and returns
    names and charcodes."""
    if not isinstance(charcodes, list):
        return False
    result = []
    for charcode, codepoint in charcodes:
        description = latexFriendlyName(Unicode[charcode])
        curcodepoint = str(codepoint)
        if private == True and charcode >= 0xE000 and charcode <= 0xF8FF:
            continue
        if description in excluded:
            continue
        result.append((curcodepoint[1:], description))
    return result


def glyphnameParse(glyphnameFile):
    """Parses glyphname file according w3c/smufl reference."""
    result = []
    with open(glyphnameFile) as json_file:
        gnames = json.load(json_file)
        for gname in gnames:
            codepoint = gnames[gname]["codepoint"].split("+")[1]
            result.append((codepoint, gname))
    return result


def defaultDescription(fontname, version):
    """Creates default description text based on name and version."""
    currentDate = datetime.today().strftime('%Y-%m-%d')
    return "%s %s LaTeX package for %s" % (currentDate, version, fontname)


def header(fontname, author):
    """Creates LaTeX Style header."""
    headstr = """
%% %s Font Package
%%
%% (c) 2020 %s
%%
%%%% This program can be redistributed and/or modified under the terms
%%%% of the LaTeX Project Public License Distributed from CTAN archives
%%%% in directory macros/latex/base/lppl.txt.
%%
""" % (fontname, author)
    return headstr


def packageName(fontname, description):
    """Creates LaTeX package descriotn and header."""
    pkgstr = """
\\ProvidesPackage{%s}
  [%s]
""" % (fontname, description)
    return pkgstr


def packageRequirements(requirements):
    """Creates LaTeX package requirements. By default fontspec is nessessary."""
    reqstr = "\\RequirePackage{fontspec}"
    if not isinstance(requirements, list):
        return reqstr
    for pkg in requirements:
        if pkg == "fontspec":
            continue
        reqstr += "\\RequirePackage{"+pkg+"}"
    return reqstr


def fontNameNormalize(fontname, prefix=True):
    """Removes spaces and forces lowercase for font name, by default adds prefix
    'fnt' so we can avoid issues with simmilar names in other LaTeX packages."""
    result = fontname.lower().replace(" ", "")
    if prefix == True:
        return "fnt"+result
    return result


def importFont(fontname, fontfile, path):
    """Creates LaTeX definitions for importing a font."""
    return "\\newfontfamily\\"+fontNameNormalize(fontname)+"{"+fontfile+"}[Path=./"+path+"/]"


def createCommandNames(fontname):
    """Creates command name, definition and command."""
    defCmd = "Define"+fontname
    return (defCmd, fontname)


def initCommands(defCommand, command, cmdPrefix):
    """Provides initialization commands for font."""
    cmdStr = """
\\newcommand{\\%s}[2]{%%
  \\expandafter\\newcommand\\csname %s#1\\endcsname{#2}%%
}
\\newcommand{\\%s}[1]{\\makeatletter \\%s \\csname %s#1\\endcsname \\reset@font\\makeatother}
""" % (defCommand, cmdPrefix, command, cmdPrefix, cmdPrefix)
    return cmdStr


def preparePackage(fontfile, author, description, requirements=[]):
    """Prepares LaTeX package header, initialization commands and requirements."""
    result = ""
    # command names, normalized and definitions.
    #fontNormalized = fontNameNormalize(fontname)
    fontname = fontName(fontfile)
    cmds = createCommandNames(fontname)
    filename = os.path.basename(fontfile)
    filepath = os.path.dirname(fontfile)
    # creates header commends.
    result = header(fontname, author)
    # creates package name definition.
    result += "\n" + packageName(fontname, description)
    # creates package requirements.
    result += "\n" + packageRequirements(requirements)
    # imports font (uses fontspec).
    result += "\n" + importFont(fontname, filename, filepath)
    # creates intial commands.
    result += "\n" + \
        initCommands(cmds[0], cmds[1], fontNameNormalize(fontname, True))

    return result


def validateNormalize(arguments):
    """Validates and normalizes provided arguments."""
    optionals = dict()
    optionals["name"] = arguments.name
    optionals["version"] = arguments.ver
    optionals["description"] = arguments.description
    optionals["author"] = arguments.author

    if optionals["version"] == None:
        optionals["version"] = "v.0.1"
    if optionals["author"] == None:
        optionals["author"] = __author__
    return optionals


def retrieveCodes(filepath, smufl):
    """Retrieves the codepoints and symbols for the desired font, handles
    differently if its smufl font."""
    if smufl != None and checkJson(smufl) == False:
        raise Exception("Error! Please provide a valid smufl json file")
    elif smufl != None and checkJson(smufl) == True:
        return glyphnameParse(smufl)
    else:
        charcodes = fontCodepoints(filepath)
        charcodes = fontNormalize(charcodes, excluded=["????"])
        if isinstance(charcodes, list):
            return charcodes
        else:
            raise Exception("Uknown font parse error")


def createLaTexCommands(charcodes, fontfile):
    """Generates LaTeX commands for each char code."""
    if not isinstance(charcodes, list):
        return False
    fontname = fontName(fontfile)
    cmds = createCommandNames(fontname)
    commands = "\n"
    for codepoint, desc in charcodes:
        commands += "\\"+cmds[0]+"{"+desc+"}{\\char\""+codepoint+"\\relax}\n"
    if commands == "\n":
        raise Exception("Error. Cannot create LaTeX style commands")
    return commands


def writePackage(fontname, code):
    """Writes Style file."""
    sty = open(fontname+".sty", "w")
    sty.write(code)
    sty.close()


def createStyleFile(font, author, description, version, smufl):
    """ Creates LaTeX Style file."""
    charcodes = retrieveCodes(font, smufl)
    if description == None:
        description = defaultDescription(fontName(font), version)
    header = preparePackage(font, author, description)
    latexCommands = createLaTexCommands(charcodes, font)

    return font, (header + latexCommands)


def handleFolder(path, author, description, version, smufl):
    """Iterates through provided path and returns fontfiles and style files
    content."""
    fonts = getFontsByType(path)
    result = []
    fontfiles = []
    for font in fonts:
        _, sty = createStyleFile(font, author, description, version, smufl)
        result.append(sty)
        fontfiles.append(font)
    return fontfiles, result

def singlePackage(fontfile,content):
    """Creates a single package folder and its files."""
    fontname = fontName(fontfile)
    createDir(fontname)
    packageFontsPath = fontname + "/fonts"
    createDir(packageFontsPath)
    shutil.copy2(fontfile,packageFontsPath)
    writePackage(fontname+"/"+fontname, content)

def createPackage(fontfiles, content):
    """Creates the final package with style and font files."""
    if isinstance(fontfiles, list) and isinstance(content, list):
        for font in fontfiles:
            for style in content:
                singlePackage(font,style)
    elif isinstance(fontfiles, str) and isinstance(content, str):
        singlePackage(fontfiles,content)
    else:
        raise Exception("Error, cannot save files.")

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
    parser.add_argument('--name', '-n', type=str,
                        help='In case of single font provided forces specified name. Otherwise %(prog)s detects the name from file.')
    parser.add_argument('--description', type=str,
                        help='LaTeX Style package description. It is ignored in case of --all flag.')
    parser.add_argument('--author', type=str, help='Author\'s name.')
    parser.add_argument('--ver', type=str, help='LaTeX package version.')
    args = parser.parse_args()

    if isdir(args.path) == False and isfile(args.path) == False:
        raise Exception("Error! First argument must be file or directory.")

    # Normalize and validate optional values
    optionals = validateNormalize(args)

    # Handles different cases of command.
    # In case of "all" flag we create styles for every font in folder. For both
    # "all" true/false createPackage handles the package creation and
    # createStyleFile the LaTeX style content.
    if args.all == True and isdir(args.path) == False:
        raise Exception(
            "Error! flag --all must be defined along with directory only!")

    if args.all == True and isdir(args.path) == True:
        fontfiles, result = handleFolder(args.path, optionals["author"],
                                         optionals["description"], optionals["version"],
                                         args.smufl)
    if args.all == False and isfile(args.path) == True:
        fontfiles, result = createStyleFile(args.path, optionals["author"],
                                            optionals["description"], optionals["version"],
                                            args.smufl)
    # Create LaTeX package(s).
    createPackage(fontfiles, result)


if __name__ == "__main__":
    main()
