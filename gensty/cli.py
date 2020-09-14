# -*- coding: utf-8 -*-
"""Gensty main file for CLI manipulation.
Latex package generator ttf/otf and SMuFL."""
import os
import sys
import shutil
import argparse
from gensty.helpers import checkExtension, createDir, writePackage, checkFont
from gensty.helpers import getFontsByType
from gensty.config import __version__, FONTDIR, SUPPORTED_FONTS
from gensty.font import LaTeXstyle
from datetime import datetime
from typing import Tuple, List


def __saveSinglePackage(fontname: str, fontpath: str, content: str):
    """__saveSinglePackage. Creates a single package folder and its files and
    save thes to disk.

    Args:
        fontname (str): The font name.
        fontpath (str): The path to font file.
        content (str): LaTeX Style content.
    """
    createDir(fontname)
    packageFontsPath = fontname + "/" + FONTDIR
    createDir(packageFontsPath)
    shutil.copy2(fontpath, packageFontsPath)
    writePackage(fontname+"/"+fontname, content)


def prepareFonts(path: str, ver: str = None, author: str = None,
                 smufl: str = None) -> List[LaTeXstyle]:
    """prepareFonts. Creates font.latexStyle instances in a list.

    Args:
        path (str): Either font(s) path directory or path to font file.
        ver (str, optional): LaTeX package version.
        author (str, optional): Latex package author.
        smufl (str, optional): SMuFL glyphnames.json definition.
    Returns:
        A list of :func:`~gensty.font.LaTeXstyle` instances containing all data
        needed final package generation.
    """
    fonts = []

    if os.path.isdir(path) == True:
        fontfiles = getFontsByType(path, SUPPORTED_FONTS)
        for ffile in fontfiles:
            fonts.append(LaTeXstyle(
                version=ver, author=author, fontfile=ffile, smufl=smufl))
    elif checkFont(path, SUPPORTED_FONTS) == True:
        fonts.append(LaTeXstyle(
            version=ver, author=author, fontfile=path, smufl=smufl))
    else:
        raise Exception("Unhandled operation!")
    return fonts


def makePackage(fonts: str, packageName: str = None, forcedCommand: str = None) -> Tuple[List[str], List[str], List[str]]:
    """makePackage.

    Args:
        fonts (str): Font(s) path, either a file path or directory.
        packageName (str, optional): Forced package name which overrides the
        font name in folders and paths.
        forcedCommand (str, optional): Overrides the name of generated
        LaTeX command.

    Returns:
        Three lists (triplet) of string containing Fontnames, Filenames and
        actual LaTeX style files.
    """
    if not isinstance(fonts, list) or len(fonts) == 0:
        raise Exception("Error. Please provide list of LaTeXstyle instances!")

    files = []
    fontfiles = []
    names = []
    if packageName != None and packageName != "":
        header = ""
        defcommands = ""
        commands = ""
        for pkg in fonts:
            pkg.setPackage(packageName)
            pkg.setCommand(forcedCommand)
            header = pkg.Header()
            defcommands += pkg.DefCommands()
            commands += pkg.Commands()
            fontfiles.append(pkg.fontfile)
            names.append(pkg.name)
        files.append(header + defcommands + commands)
    else:
        for pkg in fonts:
            pkg.setCommand(forcedCommand)
            header = pkg.Header()
            defcommands = pkg.DefCommands()
            commands = pkg.Commands()
            files.append(header + defcommands + commands)
            fontfiles.append(pkg.fontfile)
            names.append(pkg.name)

    return names, fontfiles, files


def savePackage(names: list, fontfiles: list, files: list, packageName:str = None):
    """savePackage. Saves packages to disk, creating the appropriate folder
    structure. There are four cases:

    - Single font. Simplest form creates one package.
    - Multiple font. Creates one package per font (incl. font file)
    - Single font, named package. Overrides the default font name on folders.
    - Multiple font, named package. Saves all fonts in same dir.

    Args:
        names (list): A list of  `str`
        fontfiles (list): fontfiles
        files (list): files
        packageName (str): packageName
    """
    if packageName != None and packageName != "":
        createDir(packageName)
        fontpath = packageName + "/" + FONTDIR
        createDir(fontpath)
        if len(fontfiles) > 0 and len(files) > 0:
            for idx, font in enumerate(fontfiles):
                shutil.copy2(font, fontpath)
                if idx in range(-len(files), len(files)):
                    writePackage(packageName+"/"+packageName, files[idx])
        else:
            raise Exception("Unknown Error!")
    else:
        for idx, pkg in enumerate(files):
            __saveSinglePackage(names[idx], fontfiles[idx], pkg)


def cli():
    """cli. Handles console arguments."""
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

    if checkFont(args.path, SUPPORTED_FONTS) == False and os.path.isdir(args.path) == False:
        raise Exception(
            "Error! path should be a valid font file (%s) or directory."
            % ','.join(SUPPORTED_FONTS))

    if args.smufl != None and checkExtension(args.smufl, "json") == False:
        raise Exception("Error! Please provide a valid smufl json file")

    # prepare fonts.
    fonts = prepareFonts(args.path, args.ver, args.author, args.smufl)
    fontnames, fontfiles, files = makePackage(
        fonts, args.one_package, args.force_name)
    # creates font package with folder stracture etc.
    savePackage(fontnames, fontfiles, files, packageName=args.one_package)
