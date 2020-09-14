# -*- coding: utf-8 -*-
import os
import json
from fontTools.unicode import Unicode
from fontTools import ttLib
from datetime import datetime
from gensty.helpers import ReplaceToken, checkExtension, checkFont, fixString
from gensty.config import FONTDIR, SUPPORTED_FONTS, COMMANDS_TEMPLATE, HEADER_TEMPLATE
from gensty.config import LATEX_REQUIREMENTS, __author__
from typing import Tuple, List


class Info:
    """Info. Handles opentype fonts (otf, ttf) and creates codepoint/symbol
    (unicode) List of Tuples based either on sMuFL glyphnames.json file or the
    font itself as parsed by fontTools. Additionally the Class retrieves the
    font name.

    Attributes:
        fontfile (str): The font file (otf,ttf).
        name (str): The font name as retrieved from font file.
        codepoints (List[Tuple[str,str]]): Codepoints and Symbol.
        errors (List[str]): List of error messages.
    """

    def __init__(self, fontfile: str, smufl: str = None) -> None:
        """__init__. Constructor.

        Args:
            fontfile (str): The font file.
            smufl (str,optional): sMuFL glyphnames.json file.

        Returns:
             Constructor.
        """
        self.errors: list = []
        self.fontfile: str = fontfile
        if checkFont(fontfile, SUPPORTED_FONTS) == False:
            self.errors.append("Could not file font file, or not supported")
            pass
        self.__smufl: str = smufl
        self.name: str = self.__getName()
        self.codepoints: str = self.Codepoints()

    def __getName(self) -> str:
        """__getName. Get the name from the font's names table. Customized
        function based on original retrieved from: https://bit.ly/3lS4nMO

        Returns:
            Font name.
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
        name = name.decode('utf-8')
        return name.replace(" ", "").replace("-", "")

    def __glyphnameParse(self) -> List[Tuple[str, str]]:
        """__glyphnameParse. Parses glyphname file according w3c/smufl
        reference.

        Returns:
            A list of  codepoint and their description.
        """
        result = []
        with open(self.__smufl) as json_file:
            gnames = json.load(json_file)
            for gname in gnames:
                codepoint = gnames[gname]["codepoint"].replace("U+", "")
                result.append((int(codepoint, 16), gname))
        return result

    def __fontCodepoints(self) -> List[Tuple[int, str]]:
        """__fontCodepoints. Creates a list of codepoints and names for every
        character/symbol in the given font.

        Returns:
            A list of Tuples with condpoints and UTF-8 description.
        """
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

    def __fontCharList(self, charcodes: list, private: bool = False,
                       excluded: list = []) -> List[Tuple[str, str]]:
        """__fontCharList. Accepts list of tuples with charcodes and codepoints
        and returns names and charcodes.

        Args:
            charcodes (list): Codepoints/Symbols created by
            func:`~gensty.font.LaTeXstyle.__fontCodepoints`
            private (bool): Allow private symbols.
            excluded (list): List of excluded symbols.

        Returns:
            List of codepoints and description.
        """
        if not isinstance(charcodes, list):
            return False
        result = []
        for charcode, codepoint in charcodes:
            description = fixString(Unicode[charcode])
            if private == True and charcode >= 0xE000 and charcode <= 0xF8FF:
                continue
            if description in excluded:
                continue
            result.append((charcode, description))
        return result

    def Identifier(self, prefix: bool = True) -> str:
        """Identifier. Removes spaces and forces lowercase for font name, by
        default adds prefix 'fnt' so we can avoid issues with identical names.

        Args:
            prefix (bool): Font prefix.

        Returns:
            Font name identifier.
        """
        result = self.name.lower().replace(" ", "")
        if prefix == True:
            return "fnt"+result
        return result

    def Codepoints(self) -> List[Tuple[int, str]]:
        """Codepoints.Retrieves the codepoints and symbols for the desired font,
        handles differently if its smufl font.

        Returns:
            The final list of codepoints/description.
        """
        if self.__smufl != None and checkExtension(self.__smufl, "json") == True:
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
    """LaTeXstyle.
    """

    def __init__(self, version: str = None, author: str = None, **kwargs) -> None:
        """__init__.

        Args:
            version (str): version
            author (str): author
            kwargs:

        Returns:
            None:
        """
        fontfile = kwargs.get('fontfile', None)
        smufl = kwargs.get('smufl', None)
        Info.__init__(self, fontfile, smufl)
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
        self.__fontfileBase = os.path.basename(self.fontfile)
        self.packageName = None
        self.forcedName = None
        self.year = datetime.today().strftime('%Y')

    def setPackage(self, packageName: str) -> str:
        """setPackage.

        Args:
            packageName (str): packageName

        Returns:
            str:
        """
        self.packageName = packageName

    def setCommand(self, commandName: str) -> str:
        """setCommand.

        Args:
            commandName (str): commandName

        Returns:
            str:
        """
        self.forcedCommand = commandName

    def __description(self) -> str:
        """Creates default description text based on name and version."""
        currentDate = datetime.today().strftime('%Y-%m-%d')
        return "%s %s LaTeX package for %s" % (currentDate, self.version, self.name)

    def __requirements(self, requirements: list = []) -> str:
        """Creates LaTeX package requirements. By default fontspec is nessessary."""
        reqstr = ""
        if not isinstance(requirements, list):
            return reqstr
        reqstr = ""
        for pkg in requirements:
            reqstr += "\\RequirePackage{"+pkg+"}"
        return reqstr

    def __defcommands(self) -> str:
        """Creates command name, definition and command."""

        if self.forcedName != None:
            defCmd = "Define"+self.forcedName
            return (defCmd, self.forcedName)

        defCmd = "Define"+self.name
        return (defCmd, self.name)

    def __makeTemplate(self, template: str, tokens: str) -> str:
        """Parses and replace tokens in template string."""
        genstyPath = os.path.abspath(os.path.dirname(__file__))
        with open(genstyPath+"/"+template) as templateFile:
            template = templateFile.read()
            output = ReplaceToken(tokens, template)
        return output

    def Header(self) -> str:
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

    def DefCommands(self) -> str:
        """Fills Commands definition style partial."""
        defcommand, command = self.__defcommands()
        tokens = {
            'fontfile': self.__fontfileBase,
            'fontspath': FONTDIR,
            'fontfamily': self.Identifier(),
            'fntidentifier': self.Identifier(),
            'defcommand': defcommand,
            'command': command,
        }
        return self.__makeTemplate(COMMANDS_TEMPLATE, tokens)

    def Commands(self) -> str:
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

    def File(self) -> str:
        """File.

        Args:

        Returns:
            str:
        """
        header = self.Header()
        definitions = self.DefCommands()
        commands = self.Commands()
        return header + definitions + commands
