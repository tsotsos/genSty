.. gensty documentation master file, created by
   sphinx-quickstart on Thu Sep 10 18:53:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gensty's documentation!
==================================

GenSty is a LaTex style package generator for OpenType fonts (otf/ttf) which 
supports W3C SMuFL notation. With gensty you can generate your LaTeX package 
based on any OpenType font; the generator parses ttf/otf files and creates
LaTeX commands for all Unicode Symbols. 
In the case of SMuFL fonts, you can also include the glyphnames.json file, 
so it will create friendlier names and include “Private Use” symbols.

`SMuFL specifications <https://www.w3.org/2019/03/smufl13/>`_


.. toctree::
   :caption: Table of Contents
   :name: mastertoc
   :maxdepth: 4

   Readme<README>

.. toctree::
   :caption: Gensty Documentation
   :maxdepth: 2

   gensty_font
   gensty_helpers
   gensty_cli

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
