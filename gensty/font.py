import json
import gensty.helpers as helpers
from fontTools import ttLib
from fontTools.unicode import Unicode


class Info:
    def __init__(self, fontfile, smufl=None):
        self.fontfile = fontfile
        self.smufl = smufl
        self.name = self.__getName()
        self.codepoints = self.Codepoints()
        self.errors = []

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
            description = helpers._fixString(Unicode[charcode])
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
        if self.smufl != None and helpers._checkExtension(self.smufl, "json") == True:
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
    def __init__(self, **kwds):
        Info.__init__(self, **kwds)
        self.Lname = self.name

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
            commands += "\\"+cmds[0] + \
                "{"+desc+"}{\\symbol{"+str(codepoint)+"}}\n"
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
