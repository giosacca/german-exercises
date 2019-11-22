""" configuration module

A module used to manage the configuration of this package.
"""

import configparser as cp

import german as g

CONFIGURATION = \
    r'C:/Users/giova/Repos/german-exercises/german/config.ini'

class Configuration(object):
    """
    A class that represents the configuration of the package.

    Attributes
    ----------
    path : string
        The path to the configuration file.
    parser : configparser.ConfigParser
        The parser to read the configuration file.
    """

    def __init__(self, path = CONFIGURATION):

        self.path = path

        self.load_configuration()

    def load_configuration(self):
        """
        Loads the configuration from the configuration file.
        """

        self.parser = cp.ConfigParser()
        self.parser.read(self.path)

