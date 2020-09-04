import json
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

print(header("Bravura","Georgios Tsotsos"))

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

