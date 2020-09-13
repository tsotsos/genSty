import os
import sys
import shutil

def isFontPath(path):
    """ Checks if the path is file or folder. In case of folder returns all
    included fonts."""
    if os.path.isfile(path):
        return True
    elif os.path.isdir(path):
        return False
    else:
        raise Exception("Error. Path must be a valid file or folder.")


def findByExt(path, ext):
    """Finds file by extension. Returns list."""
    files = []
    if os.path.isfile(path) == True:
        if checkExtension(path, ext) == True:
            files.append(path)
        else:
            return False
    else:
        for file in os.listdir(path):
            if file.endswith("."+ext):
                files.append(os.path.join(path, file))
    return files


def createDir(dir):
    """Forces directory creation by removing any pre-existing folder with same
    name."""
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def checkExtension(path, ext):
    """Defines if a file exists and its json."""
    if not os.path.isfile(path):
        return False
    if not path.endswith("."+ext):
        return False
    return True


def writePackage(fontname, code):
    """Writes Style file."""
    sty = open(fontname+".sty", "w")
    sty.write(code)
    sty.close()


def ReplaceToken(dict_replace, target):
    """Based on dict, replaces key with the value on the target."""

    for check, replacer in list(dict_replace.items()):
        target = target.replace("["+check+"]", replacer)

    return target


def getFontsByType(path,supported_fonts=[]):
    """Gets supported fonts by file extesion in a given folder."""
    files = []
    for ext in supported_fonts:
        fonts = findByExt(path, ext)
        if not isinstance(fonts, list):
            continue
        for font in fonts:
            files.append(font)

    return files

def fixString(s):
    """Changes a string usually package or font name, so it can be use in
    LaTeX and parsed without issue."""
    return(" ".join(x.capitalize() for x in s.split(" ")).replace(" ", "").replace("-", ""))


