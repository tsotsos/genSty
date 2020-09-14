# -*- coding: utf-8 -*-
"""Gensty helpers. A collection of functions to manipulate strings, search for
files and create folders."""
import os
import sys
import shutil
from typing import Tuple, List, Union


def isFontPath(path):
    """ Checks if the path is file or folder. In case of folder returns all
    included fonts."""
    if os.path.isfile(path):
        return True
    elif os.path.isdir(path):
        return False
    else:
        raise Exception("Error. Path must be a valid file or folder.")


def findByExt(path: str, ext: str) -> Union[List[str], bool]:
    """findByExt.Finds file by extension. Returns list.

    Args:
        path (str): File path to check.
        ext (str): File extension.

    Returns:
        A list of files having the given `ext` or False.
    """
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


def createDir(dir: str):
    """createDir. Forces directory creation by removing any pre-existing folder
    with same name.

    Args:
        dir (str): Directory to create.
    """
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def checkFont(path: str, supported_fonts: list = []) -> bool:
    """checkFont. Checks the provided file has one fo the supported extensions.

    Args:
        path (str): File path to check.
        supported_fonts (list): Supported fonts `extensions`

    Returns:
        True in case font exists.
    """
    for ext in supported_fonts:
        if checkExtension(path, ext) == True:
            return True
    return False


def checkExtension(path: str, ext: str) -> bool:
    """checkExtension. Defines if a file exists and having the given `extension`.

    Args:
        path (str): File path to check.
        ext (str): File extension.

    Returns:
        True in case extension is correct.
    """
    if not os.path.isfile(path):
        return False
    if not path.endswith("."+ext):
        return False
    return True


def writePackage(filename: str, content: str):
    """writePackage. Writes Style file.

    Args:
        filename (str): Filename for newely created file.
        content (str): Content of the LaTeX package.
    """
    sty = open(filename+".sty", "w")
    sty.write(content)
    sty.close()


def ReplaceToken(dict_replace: dict, target: str) -> str:
    """ReplaceToken. Based on dict, replaces key with the value on the target.

    Args:
        dict_replace (dict): Dictionary includes tokens to replace.
        target (str): String to be replced.

    Returns:
        String with provided parameters from tokens.
    """

    for check, replacer in list(dict_replace.items()):
        target = target.replace("["+check+"]", replacer)

    return target


def getFontsByType(path: str, supported_fonts: list = []) -> List[str]:
    """getFontsByType. Gets supported fonts by file extesion in a given folder.

    Args:
        path (str): Directory includes fonts.
        supported_fonts (list): A list of supported fonts (extensions)

    Returns:
        File paths of supported fonts.
    """
    files = []
    for ext in supported_fonts:
        fonts = findByExt(path, ext)
        if not isinstance(fonts, list):
            continue
        for font in fonts:
            files.append(font)

    return files


def fixString(s: str) -> str:
    """fixString. Changes a string usually package or font name, so it can be
    use in LaTeX and parsed without issue.

    Args:
        s (str): String to be fixed.
    """
    return(" ".join(x.capitalize() for x in s.split(" ")).replace(" ", "").replace("-", ""))
