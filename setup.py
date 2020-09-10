#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from gensty import __version__
from gensty import __author__
from gensty import __email__

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='gensty',
    version=__version__,
    description='LaTex style generator for ttf/otf fonts. Supports Smufl.',
    long_description= readme,
    long_description_content_type='text/markdown',
    author=__author__,
    author_email=__email__,
    python_requires='>=3',
    url='https://github.com/tsotsos/gensty',
    packages=[
        'gensty',
    ],
    package_dir={'gensty': 'gensty'},
    include_package_data=True,
    entry_points = {
        'console_scripts': ['gensty=gensty.gensty:main'],
    },
    install_requires=['fontTools'],
    license='GPL-2.0 License',
    zip_safe=False,
    keywords='latex generator package fonts',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
    ],
)
