import os
import json
from datetime import datetime
import sys

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


allfonts = getFontsByType("fonts")
print(allfonts)
print(defaultDescription(allfonts[0],"v.0.1"))
sty = preparePackage("BravuraText","Georgios Tsotsos", "2020-09-03 v0.01 LaTeX package for BravuraText",None,allfonts[0])
print(sty)


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

