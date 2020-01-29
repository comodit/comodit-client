# dispatch.py - Command line dispatching for Cortex.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import sys
import traceback

from comodit_client.api.exporter import ExportException
from comodit_client.api.importer import ImportException
from comodit_client.control.store import AppStoreController, DistStoreController

from .api import Client
from .api.exceptions import PythonApiException
from .config import Config, ConfigException
from .control import router
from comodit_client.control.applications import ApplicationsController
from .control.distributions import DistributionsController
from .control.environments import EnvironmentsController
from .control.exceptions import ControllerException, ArgumentException
from .control.flavors import FlavorsController
from .control.hosts import HostsController
from .control.organizations import OrganizationsController
from .control.platforms import PlatformsController
from .rest.exceptions import ApiException
from .util.editor import NotModifiedException
import comodit_client.version as version


def run(argv):
    # entities
    router.register(["flavors"], FlavorsController())
    router.register(["platforms"], PlatformsController())
    router.register(["applications"], ApplicationsController())
    router.register(["distributions"], DistributionsController())
    router.register(["organizations"], OrganizationsController())
    router.register(["environments"], EnvironmentsController())
    router.register(["hosts"], HostsController())
    router.register(["app-store"], AppStoreController())
    router.register(["dist-store"], DistStoreController())
    
    _parse(argv)

def _get_all_options(parser):
    options = []
    for o in parser._option_string_actions:
        options.append(o)
    return options

def _get_value_options(parser):
    # TODO : automatically detect value options
    options = [
                "-f", "--file",
                "-j", "--json",
                "--api",
                "--user",
                "--pass",
                "--token",
                "--templates",
                "--profile",
                "--completions",
                "--org",
                "--flavor",
                "--with-org",
                "--no-delete"
                ]
    return options


def __get_parser(config):
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                     description = "This is the ComodIT CLI.",
                                     epilog = """\
For additional help on a particular collection, just call the client giving
as argument the entity and/or see man page.

Available entities:
    platforms         Underlying infrastructure platforms
    applications      Recipes to provision and configure applications on a
                      host
    distributions     Recipes to provision and configure distributions on a
                      host
    organizations     Top-level organization
    environments      Environment defined within an organization
    hosts             Host defined within an environment
    flavors           Available flavors when creating a distribution
""")

    parser.add_argument("entity", help = "An entity")
    parser.add_argument("subentities", help = "Optional subentities", nargs = "*")
    parser.add_argument("action", help = "An action to perform on given (sub)entity", nargs = "?")

    parser.add_argument("-f", "--file", dest = "filename", help = "input file with a JSON object")
    parser.add_argument("--stdin", dest = "stdin", help = "input read from standard input", action = "store_true", default = False)
    parser.add_argument("-j", "--json", dest = "json", help = "input JSON object via command line")
    parser.add_argument("-d", "--default", dest = "default", help = "let driver setup platform upon creation", action = "store_true", default = False)
    parser.add_argument("-t", "--test", dest = "test", help = "let driver test platform upon creation", action = "store_true", default = False)
    parser.add_argument("-p", "--populate", dest = "populate", help = "organization is populated at creation time", action = "store_true", default = False)
    parser.add_argument("--raw", dest = "raw", help = "output the raw JSON results", action = "store_true", default = False)
    parser.add_argument("--secret", dest = "secret", help = "filter to get only secret setting", action = "store_true", default = False)
    parser.add_argument("--non-secret", dest = "non_secret", help = "filter to get only non secret setting", action = "store_true", default = False)
    parser.add_argument("--key", dest = "key", help = "filter to get setting by key", default = None)
    parser.add_argument("--obfuscate", dest = "obfuscate", help = "obfuscate all password", action = "store_true", default = False)
    parser.add_argument("--wait", dest = "wait", help = "wait action run is finished", action = "store_true", default = False)
    parser.add_argument("--timeout", dest = "timeout", help = "set timeout in second for wait", default = 0)
    parser.add_argument("--flavor", dest = "flavor", help = "provide distribution's flavor upon creation", default = None)

    parser.add_argument("--skip-chown", dest = "skip_chown", help = "Do not chown files on render tree", action = "store_true", default = False)
    parser.add_argument("--skip-chmod", dest = "skip_chmod", help = "Do not chmod files on render tree", action = "store_true", default = False)

    parser.add_argument("--skip-conflict", dest = "skip_conflict", help = "Skip conflicts on import", action = "store_true", default = False)
    parser.add_argument("--update-existing", dest = "update_existing", help = "Updates existing entities on import", action = "store_true", default = False)
    parser.add_argument("--dry-run", dest = "dry_run", help = "Dry-run for import of organization", action = "store_true", default = False)
    parser.add_argument("--with-instances", dest = "with_instances", help = "Imports instances as well when importing an organization, an environment or a host", action = "store_true", default = False)
    parser.add_argument("--insecure", dest = "insecure", help = "Tells the client to ignore self-signed certificates", action = "store_true", default = False)

    parser.add_argument("--public", dest = "public", help = "List only public apps/dists", action = "store_true", default = False)
    parser.add_argument("--private", dest = "private", help = "List only private apps/dists", action = "store_true", default = False)
    parser.add_argument("--featured", dest = "featured", help = "List only featured apps/dists", action = "store_true", default = False)
    parser.add_argument("--org", dest = "org_name", help = "Set organization", default = None)
    parser.add_argument("--with-org", dest = "with_org", help = "Show organization name when listing apps/dists in store", action = "store_true", default = False)

    parser.add_argument("--api", dest = "api", help = "endpoint for the API", default = None)
    parser.add_argument("--user", dest = "username", help = "username on comodit server", default = None)
    parser.add_argument("--pass", dest = "password", help = "password on comodit server", default = None)
    parser.add_argument("--token", dest = "token", help = "application key token", default = None)
    parser.add_argument("--templates", dest = "templates_path", help = "directory containing JSON templates", default = config.templates_path)
    parser.add_argument("--profile", dest = "profile_name", help = "Name of profile to use", default = None)

    parser.add_argument("--force", dest = "force", help = "bypass change management and update everything", action = "store_true", default = False)
    parser.add_argument("--debug", dest = "debug", help = "display debug information", action = "store_true", default = False)
    parser.add_argument("--version", dest = "version", help = "display version information", action = "store_true", default = False)
    parser.add_argument("--no-delete", dest = "no_delete", help = "Skips deletions when changing settings", action = "store_true", default = False)

    return parser


def _parse(argv):

    # Load configuration file
    try:
        config = Config()
    except ConfigException as e:
        print("Configuration error:")
        print(e.msg)
        exit(-1)

    # Create parser
    parser = __get_parser(config)

    # Check for completion related call
    if "--options" in argv:
        for o in _get_all_options(parser):
            print(o)
        exit(0)

    if "--options-with-value" in argv:
        for o in _get_value_options(parser):
            print(o)
        exit(0)

    try:
        completions_index = argv.index("--completions")
        del argv[completions_index]
        config.param_completions = int(argv[completions_index])
        del argv[completions_index]

        if config.param_completions == 0:
            router.print_keywords()
            exit(0)

        config.param_completions -= 1
    except Exception:
        config.param_completions = -1

    if "--version" in argv:
        print("ComodIT command line client " + version.VERSION + "-" + version.RELEASE + ".")
        exit(0)

    # Parse arguments
    config.options = parser.parse_known_args(args = argv)[0]

    # Use profile data to configure server API connector. Options provided
    # on command-line have priority.
    if config.options.api:
        api = config.options.api
    else:
        api = config.get_api(config.options.profile_name)
        config.options.api = api

    define_credentials_item('username', 'COMODIT_USERNAME')
    define_credentials_item('password', 'COMODIT_PASSWORD')
    define_credentials_item('token', 'COMODIT_TOKEN')

    if not is_credentials_defined():
        print("You have to provider either a username and a password or a token")
        exit(-1)

    client = Client(api, config.options.username, config.options.password, config.options.token, config.options.insecure)

    entity_args = [] + config.options.subentities

    if not config.options.action is None:
        entity_args.append(config.options.action)

    _dispatch(config.options, entity_args, client)


def define_credentials_item(item_name, env_name):
    config = Config()
    if not getattr(config.options, item_name):
        item_value = os.environ.get(env_name, None)
        if not item_value:
            item_value = config.get_value(config.options.profile_name, item_name, True)
        if item_value:
            setattr(config.options, item_name, item_value)


def is_credentials_defined():
    return (is_option_defined('username') and is_option_defined('password')) or is_option_defined('token')


def is_option_defined(option_name):
    config = Config()
    if hasattr(config.options, option_name):
        return getattr(config.options, option_name) is not None
    else:
        return False


def _dispatch(options, args, client):
    try:
        entity = options.entity
        router.dispatch(entity, client, args)
        exit(0)
    except ControllerException as e:
        print(e.msg)
    except ArgumentException as e:
        print(e.msg)
    except ApiException as e:
        print("Error (%s): %s" % (e.code, e.message))
    except PythonApiException as e:
        print(e)
    except ImportException as e:
        print(e)
    except ExportException as e:
        print(e)
    except NotModifiedException:
        print("Command was canceled since you did not save the file")
    except Exception as e:
        if options.debug:
            print("Exception in user code.")
        else :
            print("Oops, it seems something went wrong (use --debug to learn more).")

        if options.debug:
            print('-' * 60)
            traceback.print_exc(file = sys.stdout)
            print('-' * 60)
        exit(-1)
