#from distutils.core import setup
from setuptools import setup

setup(
    name = "bytecodehacks",
    version = "April2000",
    description = "muhahaha!",
    author = "Michael Hudson",
    author_email = "mwh21@cam.ac.uk",
    url = "http://bytecodehacks.sourceforge.net",

    packages = [ "bytecodehacks",
                 "bytecodehacks.code_gen"]
    )
