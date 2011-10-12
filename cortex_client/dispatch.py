# dispatch.py - Command line dispatching for Cortex. 
# coding: utf-8
# 
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior 
# authorization from Guardis.
VERSION = "0.7.0-dev"
RELEASE = "Ongoing development"

from control.applications import ApplicationsController
from control.platforms import PlatformsController
from control.changes import ChangesController
from control.cms import CmsController
from control.distributions import DistributionsController
from control.environments import EnvironmentsController
from control.exceptions import ControllerException, ArgumentException
from control.files import FilesController
from control.hosts import HostsController
from control.organizations import OrganizationsController
from control.parameters import ParametersController
from control.provisioner import ProvisionerController
from control.settings import SettingsController
from control.sync.sync import SyncController
from control.users import UsersController
from rest.exceptions import ApiException
from util import globals
from util.editor import NotModifiedException
import optparse
import traceback
import sys
import control.router

def run(argv):
    control.router.register(["user"], UsersController())
    control.router.register(["pf",  "platforms"], PlatformsController())
    control.router.register(["app",  "applications"], ApplicationsController())
    control.router.register(["dist", "distributions"], DistributionsController())
    control.router.register(["org",  "organizations"], OrganizationsController())
    control.router.register(["env",  "environments"], EnvironmentsController())
    control.router.register(["host", "hosts"], HostsController())
    control.router.register(["prov", "provisioner"], ProvisionerController())
    control.router.register(["cms",  "configuration"], CmsController())        
    control.router.register(["sync"], SyncController())
    control.router.register(["param", "parameters"], ParametersController());
    control.router.register(["cr", "changes"], ChangesController());
    control.router.register(["settings"], SettingsController());    
    control.router.register(["files"], FilesController());    
    _parse(argv)

def _parse(argv):
            
    usage = "usage: %prog resource [command] [options]"
    parser = optparse.OptionParser(usage)

    parser.add_option("-f", "--file", dest="filename", help="input file with a JSON object")
    parser.add_option("-j", "--json", dest="json",     help="input JSON object via command line")
    parser.add_option("--raw",        dest="raw",      help="output the raw JSON results", action="store_true", default=False,)
    parser.add_option("--with-uuid",  dest="uuid",     help="references are UUID instead of paths",  action="store_true", default=False)
    
    parser.add_option("--org",        dest="org",      help="Path or UUID of the parent organization (conditioned by --with-uuid)")
    parser.add_option("--org-path",   dest="org_path", help="Path to the parent organization")
    parser.add_option("--org-uuid",   dest="org_uuid", help="UUID of the parent organization")

    parser.add_option("--env",        dest="env",      help="Path or UUID of the parent environment (conditioned by --with-uuid)")
    parser.add_option("--env-path",   dest="env_path", help="Path to the parent environment")
    parser.add_option("--env-uuid",   dest="env_uuid", help="UUID of the parent environment")

    parser.add_option("--host",        dest="host",      help="Path or UUID of the parent host (conditioned by --with-uuid)")
    parser.add_option("--host-path",   dest="host_path", help="Path to the parent host")
    parser.add_option("--host-uuid",   dest="host_uuid", help="UUID of the parent host")

    parser.add_option("--api",        dest="api",      help="endpoint for the API",      default="http://localhost:8000/api")
    parser.add_option("--user",       dest="username", help="username on cortex server", default="admin")
    parser.add_option("--pass",       dest="password", help="password on cortex server", default="secret")


    parser.add_option("--quiet",      dest="verbose",  help="don't print status messages to stdout", action="store_false", default=True)
    parser.add_option("--force",      dest="force",    help="bypass change management and update everything", action="store_true", default=False)
    parser.add_option("--debug",      dest="debug",    help="display debug information", action="store_true", default=False)    
    parser.add_option("--version",    dest="version",  help="display version information", action="store_true", default=False)
    
    (globals.options, args) = parser.parse_args()

    if globals.options.version:
        print "Cortex command line client, version " + VERSION + ", released on " + RELEASE + "."
        exit(0)  

    if (len(args) == 0):
        parser.print_help()
        print_resources()
        exit(-1)

    _dispatch(args[0], args[1:])
    
def _dispatch(resource, args):
    options = globals.options
    
    try:
        control.router.dispatch(resource, args)
        exit(0)
    except ControllerException as e:
        print e.msg
    except ArgumentException as e:
        print e.msg     
    except ApiException as e:
        print "Error (%s): %s" % (e.code, e.message)          
    except NotModifiedException:
        print "Command was canceled since you did not save the file"       
    except Exception:
        if options.debug:
            print "Exception in user code."
        else :
            print "Oops, it seems something went wrong (use --debug to learn more)."

    if options.debug:  
        print '-' * 60
        traceback.print_exc(file=sys.stdout)
        print '-' * 60
    exit(-1)
        
def print_resources():
    print '''
Resources:
    platforms           Underlying infrastructure platforms
    applications        Recipes to provision and configure applications on a host
    distributions       Recipes to provision and configure distributions on a host
    parameters          Describe parameters used in recipes
    files               Files used in recipes
    users               User accounts
    organizations       Top-level organization
    environments        Environment defined within an organization
    hosts               Host defined within an environment

Services:
    provisioner         Provision virtual machines based on a host definition
    cms                 Configuration manager
''' 
