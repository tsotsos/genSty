from fontTools.unicode import Unicode
from fontTools import ttLib
from datetime import datetime
import os
import json
import helpers
from config import FONTDIR, SUPPORTED_FONTS, COMMANDS_TEMPLATE, HEADER_TEMPLATE
from config import LATEX_REQUIREMENTS, __author__


class Info:
    def __init__(self, fontfile, smufl=None):
        self.errors = []
        self.fontfile = fontfile
        if helpers.checkFont(fontfile,SUPPORTED_FONTS) == False:
            self.errors.append("Could not file font file, or not supported")
            pass
        self.fontfileBase = os.path.basename(fontfile)
        self.smufl = smufl
        self.name = self.__getName()
        self.codepoints = self.Codepoints()

    def __getName(self):
        """Get the name from the font's names table.
        Customized function, original retrieved from: https://bit.ly/3lS4nMO
        """
        name = ""
        font = ttLib.TTFont(self.fontfile)
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

    def __glyphnameParse(self):
        """Parses glyphname file according w3c/smufl reference."""
        result = []
        with open(self.smufl) as json_file:
            gnames = json.load(json_file)
            for gname in gnames:
                codepoint = gnames[gname]["codepoint"].replace("U+", "")
                result.append((int(codepoint, 16), gname))
        return result

    def __fontCodepoints(self):
        """Creates a dict of codepoints and names for every character/symbol in the
        given font."""
        font = ttLib.TTFont(self.fontfile)
        charcodes = []
        for x in font["cmap"].tables:
            if not x.isUnicode():
                continue
            for y in x.cmap.items():
                charcodes.append(y)
        font.close()
        sorted(charcodes)
        return charcodes

    def __fontCharList(self, charcodes, private=False, excluded=[]):
        """Accepts list of tuples with charcodes and codepoints and returns
        names and charcodes."""
        if not isinstance(charcodes, list):
            return False
        result = []
        for charcode, codepoint in charcodes:
            description = helpers.fixString(Unicode[charcode])
            if private == True and charcode >= 0xE000 and charcode <= 0xF8FF:
                continue
            if description in excluded:
                continue
            result.append((charcode, description))
        return result

    def Identifier(self, prefix=True):
        """Removes spaces and forces lowercase for font name, by default adds prefix
        'fnt' so we can avoid issues with simmilar names in other LaTeX packages."""
        result = self.name.lower().replace(" ", "")
        if prefix == True:
            return "fnt"+result
        return result

    def Codepoints(self):
        """Retrieves the codepoints and symbols for the desired font, handles
        differently if its smufl font."""
        if self.smufl != None and helpers.checkExtension(self.smufl, "json") == True:
            charcodes = self.__glyphnameParse()
            if len(charcodes) == 0:
                self.errors.append("Empty glyphnames file.")
                return False
            return charcodes
        else:
            charcodes = self.__fontCodepoints()
            charcodes = self.__fontCharList(charcodes,
                                            excluded=["????", "Space"])
            if isinstance(charcodes, list):
                return charcodes
            else:
                self.errors.append("Error with parsing file.")
                return False


class LaTeXstyle(Info):
    def __init__(self, version=None, author=None, **kwargs):
        fontfile = kwargs.get('fontfile',None)
        smufl = kwargs.get('smufl',None)
        Info.__init__(self,fontfile,smufl)
        if len(self.errors) > 0:
            print(self.errors)
            pass
        if version == None:
            self.version = "v0.1"
        else:
            self.version = version
        if author == None:
            self.author = __author__
        else:
            self.author = author

        self.packageName = None
        self.forcedName = None
        self.year = datetime.today().strftime('%Y')

    def setPackage(self, packageName):
        self.packageName = packageName

    def setCommand(self, commandName):
        self.forcedCommand = commandName

    def __description(self):
        """Creates default description text based on name and version."""
        currentDate = datetime.today().strftime('%Y-%m-%d')
        return "%s %s LaTeX package for %s" % (currentDate, self.version, self.name)

    def __requirements(self, requirements=[]):
        """Creates LaTeX package requirements. By default fontspec is nessessary."""
        reqstr = ""
        if not isinstance(requirements, list):
            return reqstr
        reqstr = ""
        for pkg in requirements:
            reqstr += "\\RequirePackage{"+pkg+"}"
        return reqstr

    def __defcommands(self):
        """Creates command name, definition and command."""

        if self.forcedName != None:
            defCmd = "Define"+self.forcedName
            return (defCmd, self.forcedName)

        defCmd = "Define"+self.name
        return (defCmd, self.name)

    def __makeTemplate(self, template, tokens):
        """Parses and replace tokens in template string."""
        genstyPath = os.path.abspath(os.path.dirname(__file__))
        with open(genstyPath+"/"+template) as templateFile:
            template = templateFile.read()
            output = helpers.ReplaceToken(tokens, template)
        return output

    def Header(self):
        """Fills header style partial."""
        if self.packageName == None:
            self.packageName = self.name

        tokens = {
            'packageName': self.packageName,
            'description': self.__description(),
            'year': self.year,
            'author': self.author,
            'requirements': self.__requirements(LATEX_REQUIREMENTS)
        }
        return self.__makeTemplate(HEADER_TEMPLATE, tokens)

    def DefCommands(self):
        """Fills Commands definition style partial."""
        defcommand,command = self.__defcommands()
        tokens = {
            'fontfile': self.fontfileBase,
            'fontspath': FONTDIR,
            'fontfamily': self.Identifier(),
            'fntidentifier': self.Identifier(),
            'defcommand': defcommand,
            'command': command,
        }
        return self.__makeTemplate(COMMANDS_TEMPLATE, tokens)

    def Commands(self):
        """Generates LaTeX commands for each char code."""
        if not isinstance(self.codepoints, list):
            return False
        commands = "\n"
        defcommand, _ = self.__defcommands()
        for codepoint, desc in self.codepoints:
            commands += "\\" + defcommand + \
                "{"+desc+"}{\\symbol{"+str(codepoint)+"}}\n"
        if commands == "\n":
            return False
        return commands

    def File(self):
        header      = self.Header()
        definitions = self.DefCommands()
        commands    = self.Commands()
        return header + definitions + commands
