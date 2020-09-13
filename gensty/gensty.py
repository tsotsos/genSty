"""Gensty module - Latex package generator ttf/otf and SMuFL."""
import os
import sys
import argparse
import helpers
import config
import font
from datetime import datetime

from pprint import pprint


def prepareFonts(path, ver, author, smufl):
    """ Creates latexStyle instances in a list and returns it"""
    fonts = []

    if os.path.isdir(path) == True:
        fontfiles = helpers.getFontsByType(path, config.SUPPORTED_FONTS)
        for ffile in fontfiles:
            fonts.append(font.LaTeXstyle(
                version=ver, author=author, fontfile=ffile, smufl=smufl))
    elif helpers.checkFont(path,config.SUPPORTED_FONTS) == True:
        fonts.append(font.LaTeXstyle(
            version=ver, author=author, fontfile=path, smufl=smufl))
    else:
        raise Exception("Unhandled operation!")
    return fonts

def makePackage(fonts, packageName=None, forcedCommand=None):
    if not isinstance(fonts,list) or len(fonts) == 0 :
        raise Exception("Error. Please provide list of LaTeXstyle instances!")

    #handle single package case
    if packageName != None and packageName != "":
        header = ""
        defcommands = ""
        commands = ""
        for pkg in fonts:
            pkg.setPackage(packageName)
            if forcedCommand != None and forcedCommand != "":
                pkg.setCommand = forcedCommand
            header = pkg.Header()
            defcommands += pkg.DefCommands()
            commands += pkg.Commands()

        output = header + defcommands + commands
        print(output)


def main():
    parser = argparse.ArgumentParser(
        prog='genSty', description="LaTeX Style file generator for fonts")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + config.__version__)
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

    if helpers.checkFont(args.path, config.SUPPORTED_FONTS) == False and os.path.isdir(args.path) == False:
        raise Exception(
            "Error! path should be a valid font file (%s) or directory."
            % ','.join(config.SUPPORTED_FONTS))

    if args.smufl != None and helpers.checkExtension(args.smufl, "json") == False:
        raise Exception("Error! Please provide a valid smufl json file")

    # prepare fonts.
    fonts = prepareFonts(args.path, args.ver, args.author, args.smufl)
    makePackage(fonts, args.one_package, args.force_name)
    # creates font package with folder stracture etc.
    # savePackage(fontPackages)


if __name__ == "__main__":
    main()
