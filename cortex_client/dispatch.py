# dispatch.py - Command line dispatching for Cortex. 
# coding: utf-8
# 
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior 
# authorization from Guardis.
VERSION = "0.7.5-SNAPSHOT"
RELEASE = "** ongoing development **"

from control.applications import ApplicationsController
from control.platforms import PlatformsController
from control.changes import ChangesController
from control.distributions import DistributionsController
from control.environments import EnvironmentsController
from control.exceptions import ControllerException, ArgumentException
from control.files import FilesController
from control.hosts import HostsController
from control.organizations import OrganizationsController
from control.sync.sync import SyncController
from control.users import UsersController
from control.rendering import RenderingController

from rest.exceptions import ApiException
from util import globals
from util.editor import NotModifiedException
import optparse
import traceback
import sys
import control.router
from config import Config, ConfigException
from api.api import CortexApi
from api.exceptions import PythonApiException

def run(argv):
    # resources
    control.router.register(["users"], UsersController())
    control.router.register(["platforms"], PlatformsController())
    control.router.register(["applications"], ApplicationsController())
    control.router.register(["distributions"], DistributionsController())
    control.router.register(["organizations"], OrganizationsController())
    control.router.register(["environments"], EnvironmentsController())
    control.router.register(["hosts"], HostsController())
    control.router.register(["sync"], SyncController())
    control.router.register(["changes"], ChangesController());
    control.router.register(["files"], FilesController());

    # services
    control.router.register(["rendering"], RenderingController());

    _parse(argv)

def _get_all_options(parser):
    options = []
    for o in parser.option_list:
        for so in o._short_opts:
            options.append(so)
        for lo in o._long_opts:
            options.append(lo)
    return options

def _get_value_options(parser):
    # TODO : automatically detect value options
    options = [
                "-f", "--file",
                "-j", "--json",
                "--org",
                "--org-path",
                "--org-uuid",
                "--env",
                "--env-path",
                "--env-uuid",
                "--api",
                "--user",
                "--pass",
                "--templates",
                "--profile",
                "--completions"
                ]
    return options

def _parse(argv):

    usage = "usage: %prog (resource | service) [command] [options]"
    parser = optparse.OptionParser(usage)

    try:
        config = Config()
    except ConfigException, e:
        print "Configuration error:"
        print e.msg
        exit(-1)

    parser.add_option("-f", "--file", dest = "filename", help = "input file with a JSON object")
    parser.add_option("-j", "--json", dest = "json", help = "input JSON object via command line")
    parser.add_option("--raw", dest = "raw", help = "output the raw JSON results", action = "store_true", default = False,)
    parser.add_option("--with-uuid", dest = "uuid", help = "references are UUID instead of paths", action = "store_true", default = False)

    parser.add_option("--org", dest = "org", help = "Path or UUID of the parent organization (conditioned by --with-uuid)")
    parser.add_option("--org-path", dest = "org_path", help = "Path to the parent organization")
    parser.add_option("--org-uuid", dest = "org_uuid", help = "UUID of the parent organization")

    parser.add_option("--env", dest = "env", help = "Path or UUID of the parent environment (conditioned by --with-uuid)")
    parser.add_option("--env-path", dest = "env_path", help = "Path to the parent environment")
    parser.add_option("--env-uuid", dest = "env_uuid", help = "UUID of the parent environment")

    parser.add_option("--skip-chown", dest = "skip_chown", help = "Path to the parent environment", action = "store_true", default = False)
    parser.add_option("--skip-chmod", dest = "skip_chmod", help = "UUID of the parent environment", action = "store_true", default = False)

    parser.add_option("--api", dest = "api", help = "endpoint for the API", default = None)
    parser.add_option("--user", dest = "username", help = "username on cortex server", default = None)
    parser.add_option("--pass", dest = "password", help = "password on cortex server", default = None)
    parser.add_option("--templates", dest = "templates_path", help = "directory containing JSON templates", default = config.templates_path)
    parser.add_option("--profile", dest = "profile_name", help = "Name of profile to use", default = config.get_default_profile_name())

    parser.add_option("--quiet", dest = "verbose", help = "don't print status messages to stdout", action = "store_false", default = True)
    parser.add_option("--force", dest = "force", help = "bypass change management and update everything", action = "store_true", default = False)
    parser.add_option("--debug", dest = "debug", help = "display debug information", action = "store_true", default = False)
    parser.add_option("--version", dest = "version", help = "display version information", action = "store_true", default = False)

    parser.add_option("--options", dest = "show_options", help = "display options", action = "store_true", default = False)
    parser.add_option("--options-with-value", dest = "show_options_with_value", help = "display options", action = "store_true", default = False)
    parser.add_option("--resources", dest = "show_resources", help = "display resources", action = "store_true", default = False)
    parser.add_option("--completions", dest = "param_completions", type = "int", help = "parameter to complete", default = -1)

    (globals.options, args) = parser.parse_args()

    if globals.options.version:
        print "Cortex command line client, version " + VERSION + ", released on " + RELEASE + "."
        exit(0)

    if globals.options.show_options:
        for o in _get_all_options(parser):
            print o
        exit(0)

    if globals.options.show_options_with_value:
        for o in _get_value_options(parser):
            print o
        exit(0)

    if globals.options.show_resources:
        control.router.print_keywords()
        exit(0)

    if (len(args) == 0):
        parser.print_help()
        print_resources()
        exit(-1)

    # Use profile data to configure server API connector. Options provided
    # on command-line have priority.
    profile = config.get_profile(globals.options.profile_name)
    if globals.options.api:
        api = globals.options.api
    else:
        api = profile["api"]
        globals.options.api = api

    if globals.options.username:
        username = globals.options.username
    else:
        username = profile["username"]
        globals.options.username = username

    if globals.options.password:
        password = globals.options.password
    else:
        password = profile["password"]
        globals.options.password = password

    api = CortexApi(api, username, password)

    _dispatch(args[0], args[1:], api)

def _dispatch(resource, args, api):
    options = globals.options

    try:
        control.router.dispatch(resource, api, args)
        exit(0)
    except ControllerException as e:
        print e.msg
    except ArgumentException as e:
        print e.msg
    except ApiException as e:
        print "Error (%s): %s" % (e.code, e.message)
    except PythonApiException as e:
        print e.message
    except NotModifiedException:
        print "Command was canceled since you did not save the file"
    except Exception:
        if options.debug:
            print "Exception in user code."
        else :
            print "Oops, it seems something went wrong (use --debug to learn more)."

    if options.debug:
        print '-' * 60
        traceback.print_exc(file = sys.stdout)
        print '-' * 60
    exit(-1)

def print_resources():
    print '''
Resources:
    platforms           Underlying infrastructure platforms
    applications        Recipes to provision and configure applications on a
                        host
    distributions       Recipes to provision and configure distributions on a
                        host
    files               Files used in recipes
    users               User accounts
    organizations       Top-level organization
    environments        Environment defined within an organization
    hosts               Host defined within an environment
    changes             Change requests

Services:
    rendering           Rendering of templates
'''
