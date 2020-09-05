import os
import json
import argparse
import sys
from datetime import datetime
from fontTools import ttLib

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

def isfile (path):
    """ Detects if the given string is file."""
    if os.path.isfile(path):
        return True
    return False

def isdir (path):
    """ Detects if the given string is directory."""
    if os.path.isdir(path):
        return True
    return False


def findByExt(path,ext):
    """Finds file by extension. Returns list."""
    files = []
    for file in os.listdir(path):
        if file.endswith("."+ext):
            files.append(os.path.join(path, file))
    return files

def getFontsByType(path):
    """Gets supported fonts by file extesion in a given folder."""
    files = []
    fontExt = ["otf","ttf"]
    for ext in fontExt:
        fonts = findByExt(path,ext)
        if not isinstance(fonts,list):
            continue
        for font in fonts:
            files.append(font)

    return files

def fontName( fontfile ):
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
    #TODO: test for issues with multiple fonts
    name = name.decode('utf-8')
    return name.replace(" ","")

def defaultDescription(fontname,version):
    """Creates default description text based on name and version."""
    currentDate = datetime.today().strftime('%Y-%m-%d')
    return "%s %s LaTeX package for %s" % (currentDate, version, fontname)

def packageName(fontname,description):
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

def fontNameNormalize(fontname,prefix = True):
    """Removes spaces and forces lowercase for font name, by default adds prefix
    'fnt' so we can avoid issues with simmilar names in other LaTeX packages."""
    result = fontname.lower().replace(" ","")
    if prefix == True:
        return "fnt"+result
    return result

def importFont(fontname,fontfile,path):
    """Creates LaTeX definitions for importing a font."""
    return "\\newfontfamily\\"+fontname+"{"+fontfile+"}[Path=./"+path+"]"

def createCommandNames(fontname):
    """Creates command name, definition and command."""
    defCmd = "Define"+fontNameNormalize(fontname,False)
    cmd = fontNameNormalize(fontname,False)
    return (defCmd,cmd)

def initCommands(defCommand, command, cmdPrefix):
    """Provides initialization commands for font."""
    cmdStr = """
\\newcommand{\\%s}[2]{%%
  \\expandafter\\newcommand\\csname %s#1\\endcsname{#2}%%
}
\\newcommand{\\%s}[1]{\\makeatletter \\%s \\csname %s#1\\endcsname \\reset@font\\makeatother}
""" % (defCommand, cmdPrefix, command, cmdPrefix, cmdPrefix)
    return cmdStr

def preparePackage(fontname, author, description, requirements, fontfile):
    """Prepares LaTeX package header, initialization commands and requirements."""
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

def validateNormalize(arguments):
    """Validates and normalizes provided arguments."""
    optionals = dict()
    optionals["name"] = arguments.name
    optionals["version"] = arguments.ver
    optionals["description"] = arguments.description
    optionals["author"] = arguments.author

    if optionals["version"] == None:
        optionals["version"]= "v.0.1"
    if optionals["description"] == None:
        if optionals["name"] == None:
            optionals["description"] = None
        else:
            optionals["description"] = defaultDescription(optionals["name"],optionals["version"])
    if optionals["author"] == None:
        optionals["author"] == __author__

    return optionals

def handleFolder(path,author,description,version):
    allfonts = getFontsByType(path)
    print(fontName(allfonts[0]))
    print(allfonts)

def main():
    #allfonts = getFontsByType("fonts")
    #desc = defaultDescription(allfonts[0],"v.0.1")
    #sty = preparePackage("BravuraText","Georgios Tsotsos", desc ,None,allfonts[0])
    #print(sty)
    parser = argparse.ArgumentParser(prog='genFontSty',description="LaTeX Style file generator for fonts")
    parser.add_argument('--version','-v', action='version', version='%(prog)s '+ __version__)
    parser.add_argument('path',help='Font(s) path. It can be either a directory in case of multiple fonts or file path.')
    parser.add_argument('--all','-a', action="store_true",help='If choosed %(prog)s will generate LaTeX Styles for all fonts in directory')
    parser.add_argument('--name','-n', type=str,help='In case of single font provided forces specified name. Otherwise %(prog)s detects the name from file.')
    parser.add_argument('--description','-D', type=str,help='LaTeX Style package description.')
    parser.add_argument('--author','-A', type=str,help='Author\'s name.')
    parser.add_argument('--ver','-V', type=str,help='LaTeX package version.')
    args = parser.parse_args()

    if isdir(args.path) == False and isfile(args.path) == False:
        raise Exception("Error! First argument must be file or directory.")
    # Normalize and validate optional values
    optionals = validateNormalize(args)
    # In case of "all" flag we create styles for every font in folder
    if args.all == True and isdir(args.path) == False:
        raise Exception("Error! flag --all must be defined along with directory only!")
    if args.all == True and isdir(args.path) == True:
        handleFolder(args.path,optionals["author"],optionals["description"],optionals["version"])

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

