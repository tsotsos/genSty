import os
import json
import argparse
import sys
from datetime import datetime

__version__ = '0.1'
__author__ = 'Georgios Tsotsos'

def header(fontname,author):
    headstr = """
%% %s Font Package
%%
%% (c) 2020 %s
%%
%%%% This program can be redistributed and/or modified under the terms
%%%% of the LaTeX Project Public License Distributed from CTAN archives
%%%% in directory macros/latex/base/lppl.txt.
%%
""" % (fontname,author)
    return headstr

def findByExt(path,ext):
    files = []
    for file in os.listdir(path):
        if file.endswith("."+ext):
            files.append(os.path.join(path, file))
    return files

def getFontsByType(path):
    files = []
    fontExt = ["otf","ttf"]
    for ext in fontExt:
        fonts = findByExt(path,ext)
        if not isinstance(fonts,list):
            continue
        for font in fonts:
            files.append(font)

    return files

def defaultDescription(fontname,version):
    currentDate = datetime.today().strftime('%Y-%m-%d')
    return "%s %s LaTeX package for %s" % (currentDate, version, fontname)

def packageName(fontname,description):
    pkgstr = """
\\ProvidesPackage{%s}
  [%s]
""" % (fontname, description)
    return pkgstr

def packageRequirements(requirements):
    reqstr = "\\RequirePackage{fontspec}"
    if not isinstance(requirements, list):
        return reqstr
    for pkg in requirements:
        if pkg == "fontspec":
            continue
        reqstr += "\\RequirePackage{"+pkg+"}"
    return reqstr

def fontNameNormalize(fontname,prefix = True):
    result = fontname.lower().replace(" ","")
    if prefix == True:
        return "fnt"+result
    return result

def importFont(fontname,fontfile,path):
    return "\\newfontfamily\\"+fontname+"{"+fontfile+"}[Path=./"+path+"]"

def createCommandNames(fontname):
    defCmd = "Define"+fontNameNormalize(fontname,False)
    cmd = fontNameNormalize(fontname,False)
    return (defCmd,cmd)

def initCommands(defCommand, command, cmdPrefix):
    cmdStr = """
\\newcommand{\\%s}[2]{%%
  \\expandafter\\newcommand\\csname %s#1\\endcsname{#2}%%
}
\\newcommand{\\%s}[1]{\\makeatletter \\%s \\csname %s#1\\endcsname \\reset@font\\makeatother}
""" % (defCommand, cmdPrefix, command, cmdPrefix, cmdPrefix)
    return cmdStr

def preparePackage(fontname, author, description, requirements, fontfile):
    result = ""
    #command names, normalized and definitions.
    fontNormalized = fontNameNormalize(fontname)
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
    result += "\n" + importFont(fontNormalized,filename,filepath)
    # creates intial commands.
    result += "\n" + initCommands(cmds[0],cmds[1],fontNormalized)

    return result

def validate(arguments):
    name = arguments.name
    version = arguments.styver
    description = arguments.description
    author = arguments.author

    if version == None:
        version = "v.0.1"
    if description == None:
        description = defaultDescription(name,version)
    if author == None:
        author == __author__

    return False

def isfile (path):
    if os.path.isfile(path):
        return True
    return False

def isdir (path):
    if os.path.isdir(path):
        return True
    return False

def main():
    #allfonts = getFontsByType("fonts")
    #desc = defaultDescription(allfonts[0],"v.0.1")
    #sty = preparePackage("BravuraText","Georgios Tsotsos", desc ,None,allfonts[0])
    #print(sty)
    parser = argparse.ArgumentParser(prog='genFontSty',description="LaTeX Style file generator for fonts")
    parser.add_argument('--version','-v', action='version', version='%(prog)s '+ __version__)
    parser.add_argument('path',help='Font(s) path. It can be either a directory in case of multiple fonts or file path.')
    parser.add_argument('--all','-a', action="store_true",help='If choosed %(prog)s will generate LaTeX Styles for all fonts in directory')
    parser.add_argument('--name','-n', type=str,help='If no name defined or --all is used %(prog)s will set filename')
    parser.add_argument('--description','-D', type=str,help='LaTeX Style package description.')
    parser.add_argument('--author','-A', type=str,help='Author\'s name.')
    parser.add_argument('--ver','-V', type=str,help='LaTeX package version.')
    args = parser.parse_args()

    if isdir(args.path) == False and isfile(args.path) == False:
        raise Exception("Error! First argument must be file or directory.")

    # In case of "all" flag we create styles for every font in folder
    if args.all == True:
        print("All fonts created")

if __name__ == "__main__":
   main()

sys.exit()
commands = "\n"
commandsText = "\n"
with open('glyphnames.json') as json_file:
    gnames = json.load(json_file)
    for gname in gnames:
        codepoint = gnames[gname]["codepoint"].split("+")[1]
        commands += "\\DefineBravura{"+gname+"}{\\char\""+codepoint+"\\relax}\n"
        commandsText += "\\DefineBravuraText{"+gname+"}{\\char\""+codepoint+"\\relax}\n"

sty = open("bravura.sty", "a")
sty.write(commands)
sty.close()

sty2 = open("bravuraText.sty", "a")
sty2.write(commandsText)
sty2.close()

