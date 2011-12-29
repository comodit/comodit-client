# Setup Python path
import sys, setup, urllib2
import definitions as defs
sys.path.append("..")


#==============================================================================
# Imports section

from cortex_client.api.api import CortexApi
from cortex_client.api.exceptions import PythonApiException


#==============================================================================
# Script

def __unset_httpd_port_setting(host, conf):
    try:
        setting = conf.settings().get_resource("httpd_port")
        setting.delete()
    except PythonApiException, e:
        print e.message

def __unset_httpd_port_setting_at_app(host):
    try:
        setting = host.application_settings().get_resource("httpd_port")
        setting.delete()
    except PythonApiException, e:
        print e.message

def undo_demo():
    # API from server cortex listening on port 8000 of localhost is used
    # Username "admin" and password "secret" are used for authentification
    api = CortexApi(setup.global_vars.comodit_url, setup.global_vars.comodit_user, setup.global_vars.comodit_pass)

    org = api.organizations().get_resource(defs.global_vars.org_name)
    env = org.environments().get_resource(defs.global_vars.env_name)
    host = env.hosts().get_resource(defs.global_vars.host_name)

    print "Uninstalling web server..."
    try:
        host.uninstall_application(defs.global_vars.app_name)
    except PythonApiException, e:
        print e.message


    print "Removing httpd_port from organization..."
    __unset_httpd_port_setting(host, org)

    print "Removing httpd_port from environment..."
    __unset_httpd_port_setting(host, env)

    print "Removing httpd_port from host..."
    __unset_httpd_port_setting(host, host)


#==============================================================================
# Entry point
if __name__ == "__main__":
    setup.setup()
    defs.define()
    undo_demo()