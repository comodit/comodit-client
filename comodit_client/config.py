# coding: utf-8

"""
Cortex client configuration file parsing.
"""

import os

from future import standard_library
standard_library.install_aliases()

# Following import MUST come after call to install_aliases
from builtins import object
from builtins import str
import configparser


def singleton(cls):
    """
    Config singleton decorator
    """
    instances = {}
    def getinstance():
        """
        Returns singleton's unique instance.
        @return: A reference
        """
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class ConfigException(Exception):
    """
    Configuration exception.
    """
    def __init__(self, message):
        """
        Creates a ConfigException instance.
        @param message: A message
        @type message: String
        """
        self.msg = message

@singleton
class Config(object):
    """
    ComodIT client's configuration.
    """

    _default_config = {
        "client": {
            "default_profile": "default"
            },
        "default": {
            "api": "http://localhost:8000/api",
            "username": "admin",
            "password": "secret",
            "token": "",
            "vnc_viewer_call": "vinagre %h:%p"
            }
        }
    """
    Default configuration values
    """

    def __init__(self):
        """
        Creates a Config instance.
        """
        # load the configuration file path
        config_path = self._get_config_path()
        if not config_path:
            self.config = self._default_config
        else:
            # load the configuration file
            self.config = self._get_config_dict(config_path)
            self._check_config()

        self.default_profile_name = self.config["client"]["default_profile"]
        self.default_profile = self.config[self.default_profile_name]

        # set templates directory
        self.templates_path = self._get_templates_path()
        if not self.templates_path:
            raise IOError("No templates directory found")

    def get_value(self, profile_name, key, optional = False):
        if profile_name is None:
            profile_name = self.default_profile_name
        if profile_name not in self.config:
            raise ConfigException("No profile with name " + str(profile_name))
        profile = self.config[profile_name]
        if key not in profile:
            value = None
        else:
            value = profile[key]
        if value is None and key in self.default_profile:
            value = self.default_profile[key]

        if value is None and not optional:
            raise ConfigException("No value for key " + key)

        return value

    def get_api(self, profile_name):
        return self.get_value(profile_name, "api")

    def get_username(self, profile_name):
        return self.get_value(profile_name, "username", True)

    def get_password(self, profile_name):
        return self.get_value(profile_name, "password", True)
    
    def get_token(self, profile_name):
        return self.get_value(profile_name, "token", True)

    def get_vnc_viewer_call(self, profile_name):
        return self.get_value(profile_name, "vnc_viewer_call")

    def _check_config(self):
        """
        Checks if configuration file could be parsed and contains valid
        data.
        """

        if(self.config is None):
            raise ConfigException("Unable to parse config file")

        if "client" not in self.config:
            raise ConfigException("No client section defined")

        if "default_profile" not in self.config["client"]:
            raise ConfigException("No default_profile property defined in client section")

        default_profile = self.config["client"]["default_profile"]
        default_profile_exists = False
        for section in self.config:
            if section == "client":
                continue # client section's content has already been checked

            self._check_property(section, "api")

            if "token" not in self.config[section] and ("username" not in self.config[section] or "password" not in self.config[section]):
                raise ConfigException("Profile " + section + " should define either 'username' and 'password' properties or 'token' property")

            if section == default_profile:
                default_profile_exists = True

        if not default_profile_exists:
            raise ConfigException("Default profile is not defined")

    def _check_property(self, section, name):
        if name not in self.config[section]:
            raise ConfigException(section + " section lacks '" + name + "' property")

    def _get_config_path(self):
        """ Gets the configuration path with following priority order :
        1) <current_directory>/conf/comodit-client.conf
        2) ~/.comoditrc
        3) /etc/comodit-client/comodit-client.conf

        elsewhere : return None
        """
        config_name = "comodit-client.conf"

        curdir_path = os.curdir + "/conf/" + config_name
        user_path = os.path.expanduser("~") + "/.comoditrc"
        etc_path = "/etc/comodit-client/" + config_name

        for loc in curdir_path, user_path, etc_path:
            if os.path.isfile(loc) and os.access(loc, os.R_OK):
                return loc

        return None

    def _get_templates_path(self):
        curdir_path = os.curdir + "/templates"
        user_path = os.path.expanduser("~") + "/.comodit/templates"
        etc_path = "/usr/share/comodit-client/templates/"

        for loc in curdir_path, user_path, etc_path:
            if os.path.isdir(loc):
                return loc

        return None

    def _get_config_dict(self, config_path):
        """ Transforms the configuration file to a dict of dict
        example :

        [client]
        default_profile = default
        
        [default]
        username = foologin
        password = foopass
        token    = token
        api      = url

        becomes :

        {
            "client": {
                "default_profile": "default"
            },
            "default": {
                "api": "http://localhost:8000/api",
                "username": "admin",
                "password": "secret",
                "token": "token"
            }
        }

        """
        self.config_parser = configparser.ConfigParser(interpolation=None)
        self.config_parser.read(config_path)

        cfg = {}
        for section in self.config_parser.sections():
            cfg[section] = dict(self.config_parser.items(section))

        return cfg
