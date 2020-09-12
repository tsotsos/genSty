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
    def __init__(self,**kwds):
        Info.__init__(self,**kwds)
        self.Lname = self.name
