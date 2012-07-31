"""
Cortex client configuration file parsing.
"""

import os

import ConfigParser

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
    Cortex client's configuration.
    """

    _default_config = {
        "client": {
            "default_profile": "default"
            },
        "default": {
            "api": "http://localhost:8000/api",
            "username": "admin",
            "password": "secret",
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

        default_profile_name = self.config["client"]["default_profile"]
        self.default_profile = self.config[default_profile_name]

        # set templates directory
        self.templates_path = self._get_templates_path()
        if not self.templates_path:
            raise IOError("No templates directory found")

    def get_default_profile_name(self):
        """
        Provides default profile's name.
        @return: A profile's name
        @rtype: String
        """
        return self.config["client"]["default_profile"]

    def get_default_api(self):
        """
        Provides default profile's API URL.
        @return: A URL
        @rtype: String
        """
        return self.default_profile["api"]

    def get_default_username(self):
        """
        Provides default profile's user name.
        @return: A user name
        @rtype: String
        """
        return self.default_profile["username"]

    def get_default_password(self):
        """
        Provides default profile's password.
        @return: A password
        @rtype: String
        """
        return self.default_profile["password"]

    def get_profile(self, name):
        """
        Provides properties associated to given profile.
        @param name: A profile's name
        @type name: String
        """
        return self.config[name]

    def _check_config(self):
        """
        Checks if configuration file could be parsed and contains valid
        data.
        """

        if(self.config is None):
            raise ConfigException("Unable to parse config file")

        if not self.config.has_key("client"):
            raise ConfigException("No client section defined")

        if not self.config["client"].has_key("default_profile"):
            raise ConfigException("No default_profile property defined in client section")

        default_profile = self.config["client"]["default_profile"]
        default_profile_exists = False
        for section in self.config:
            if section == "client":
                continue # client section's content has already been checked

            section_content = self.config[section]
            for prop in ("api", "username", "password"):
                if not section_content.has_key(prop):
                    raise ConfigException(section + " section lacks '" + prop + "' property")
            if section == default_profile:
                default_profile_exists = True

        if not default_profile_exists:
            raise ConfigException("Default profile is not defined")

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
            if os.path.isfile(loc):
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
        api      = url

        becomes :

        {
            "client": {
                "default_profile": "default"
            },
            "default": {
                "api": "http://localhost:8000/api",
                "username": "admin",
                "password": "secret"
            }
        }

        """
        self.config_parser = ConfigParser.ConfigParser()
        self.config_parser.read(config_path)

        cfg = {}
        for section in self.config_parser.sections():
            cfg[section] = dict(self.config_parser.items(section))

        return cfg
