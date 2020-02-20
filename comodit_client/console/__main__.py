# coding: utf-8

from __future__ import print_function
import sys, argparse

from comodit_client.console.core import ComodITConsole
from comodit_client.config import Config, ConfigException

if __name__ == '__main__':
    # Load configuration
    try:
        config = Config()
    except ConfigException as e:
        print("Configuration error:")
        print(e.msg)
        exit(-1)

    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                     description = "This is the ComodIT console.")

    parser.add_argument('-P', "--profile", dest = "profile", help = "A profile from comoditrc file", default = None)
    parser.add_argument('-a', "--api", dest = "api", help = "URL of the API", default = None)
    parser.add_argument('-u', "--user", dest = "username", help = "username on comodit server", default = None)
    parser.add_argument('-p', "--pass", dest = "password", help = "password on comodit server", default = None)
    parser.add_argument('-i', "--insecure", dest = "insecure", help = "Tells the client to ignore self-signed certificates", action = "store_true", default = False)
    parser.add_argument('-f', "--file", dest = "file", help = "Tells the client to execute the content of given file", default = None)
    parser.add_argument('-d', "--debug", dest = "debug", help = "Tells the client to work in debug mode, causing every exception to be considered as an error", action = "store_true", default = False)

    options = parser.parse_known_args(args = sys.argv)[0]
    # Use profile data to configure connection.
    if not options.api is None:
        api = options.api
    else:
        api = config.get_api(options.profile)
        options.api = api

    if not options.username is None:
        username = options.username
    else:
        username = config.get_username(options.profile)
        options.username = username

    if not options.password is None:
        password = options.password
    else:
        password = config.get_password(options.profile)
        options.password = password

    if (username == None) or (api == None) or (password == None):
        raise Exception("No credentials found")

    console = ComodITConsole(options.debug)
    console.connect(api, username, password, options.insecure)
    if options.file is None:
        console.interact()
    else:
        console.execute_file(options.file)
