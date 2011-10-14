import os

import ConfigParser

def singleton(cls):
    """ Define the config singleton decorator
    """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class ConfigException(Exception):
    def __init__(self, message):
        self.msg = message

@singleton
class Config(object):
    _instance = None

    _default_config = {
        "client": {
            "api": "http://localhost:8000/api",
            "username": "admin",
            "password": "secret"
            }
        }

    def __init__(self):
        # load the configuration file path
        config_path = self._get_config_path()
        if not config_path:
            self.config = self._default_config
        else:
            # load the configuration file
            self.config = self._get_config_dict(config_path)
            self._check_config()

        # set templates directory
        self.templates_path = self._get_templates_path()
        if not self.templates_path:
            raise IOError("No templates directory found")

    def _check_config(self):
        if(self.config is None):
            raise ConfigException("Unable to parse config file")

        if(not self.config.has_key("client")):
            self.config["client"]= {}

        config_fields = ["api", "username", "password"]
        for field in config_fields:
            if(not self.config["client"].has_key(field)):
                self.config["client"][field] = self._default_config["client"][field]

    def _get_config_path(self):
        """ Gets the configuration path with following priority order :
        1) <current_directory>/conf/cortex-client.conf
        2) ~/.cortexrc
        3) /etc/cortex/cortex-client.conf

        elsewhere : return None
        """
        config_name = "cortex-client.conf"

        curdir_path = os.curdir + "/conf/" + config_name
        user_path = os.path.expanduser("~") + "/.cortexrc"
        etc_path = "/etc/cortex/" + config_name

        for loc in curdir_path, user_path, etc_path:
            if os.path.isfile(loc):
                return loc

        return None

    def _get_templates_path(self):
        curdir_path = os.curdir + "/templates"
        user_path = os.path.expanduser("~") + "/.cortex/templates"
        etc_path = "/etc/cortex/client/templates/"

        for loc in curdir_path, user_path, etc_path:
            if os.path.isdir(loc):
                return loc

        return None

    def _get_config_dict(self, config_path):
        """ Transforms the configuration file to a dict of dict
        example :

        [client]
        username = foologin
        password = foopass
        api      = url

        becomes :

          {
            'client': {
              'username': 'foologin',
              'password': 'foopass'
              'api': 'url'
            }
          }

        """
        self.config_parser = ConfigParser.ConfigParser()
        self.config_parser.read(config_path)

        cfg = {}
        for section in self.config_parser.sections():
            cfg[section] = dict(self.config_parser.items(section))

        return cfg