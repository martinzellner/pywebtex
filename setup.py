import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PyWebTex",
    version = "0.0.1",
    author = "Martin Zellner",
    author_email = "martin.zellner@gmail.com",
    description = ("A simple python latex web app"),
    license = "",
    keywords = "",
    url = "https://github.com/murphy2/pywebtex",
    packages=['pywebtex'],
    install_requires=[
          'pyramid',
          'pyramid_chameleon',
          'sqlalchemy'
      ],
    long_description=read('README.md'),
    classifiers=[
    ],
)