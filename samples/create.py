# Setup Python path
import sys
sys.path.append("..")
import setup
import definitions as defs



#==============================================================================
# Imports section

from cortex_client.api.api import CortexApi
from cortex_client.api.collection import ResourceNotFoundException
from cortex_client.api.settings import Setting

#==============================================================================
# Script

def create_resources():
    # API from server cortex listening on port 8000 of localhost is used
    # Username "admin" and password "secret" are used for authentification
    api = CortexApi(setup.global_vars.comodit_url, setup.global_vars.comodit_user, setup.global_vars.comodit_pass)


    ##################################################
    # Create entities (if they do not already exist) #
    ##################################################

    print "="*80
    print "Organization"
    org_coll = api.organizations()
    try:
        org = org_coll.get_resource(defs.global_vars.org_name)
        print "Organization already exists"
    except ResourceNotFoundException:
        org = create_org(api)
        print "Organization is created"
    org.show()

    app_coll = org.applications()
    for name in defs.global_vars.app_names:
        print "="*80
        print "Application " + name
        try:
            app = app_coll.get_resource(name)
            print "Application already exists"
        except ResourceNotFoundException:
            app = create_app(org, name)
            print "Application is created"
        app.show()

    print "="*80
    print "Platform"
    plat_coll = org.platforms()
    try:
        plat = plat_coll.get_resource(defs.global_vars.plat_name)
        print "Platform already exists"
    except ResourceNotFoundException:
        plat = create_plat(org)
        print "Platform is created"

    plat.show()

    print "="*80
    print "Distribution"
    dist_coll = org.distributions()
    try:
        dist = dist_coll.get_resource(defs.global_vars.dist_name)
        print "Distribution already exists"
    except ResourceNotFoundException:
        dist = create_dist(org)
        print "Distribution is created"
    dist.show()

    print "="*80
    print "Environments"
    env_coll = org.environments()
    try:
        env = env_coll.get_resource(defs.global_vars.env_name)
        print "Environment " + defs.global_vars.env_name + " already exists"
    except ResourceNotFoundException:
        env = create_env(org)
        print "Environment " + defs.global_vars.env_name + " is created"
    env.show()

    print "="*80
    print "Host"
    host_coll = env.hosts()
    try:
        host = host_coll.get_resource(defs.global_vars.host_name)
        print "Host already exists"
    except ResourceNotFoundException:
        host = create_host(env)
        print "Host is created"
    host.show()

def create_app(org, name):
    """
    Creates an application linked to given API api
    """
    app = org.new_application(name)
    app.load_json("apps/" + name + ".json")
    app.create()

    # Upload file contents
    for f in app.get_files():
        file_res = app.files().get_resource(f.get_name())
        file_res.set_content("files/" + f.get_name())

    return app

def create_plat(org):
    """
    Creates a platform linked to given API api
    """
    plat = org.new_platform(defs.global_vars.plat_name)
    plat.load_json("Local2.json")

    plat._show(4)

    plat.create()

    # Upload file contents
    for f in plat.get_files():
        f.set_content("files/" + f.get_name())

    return plat

def create_dist(org):
    """
    Creates a distribution linked to given API api
    """
    dist = org.new_distribution(defs.global_vars.dist_name)
    dist.load_json("co6.json")

    dist.create()

    for f in dist.get_files():
        f.set_content("files/" + f.get_name())

    return dist

def create_org(api):
    """
    Creates an organization linked to given API api
    """
    org = api.new_organization(defs.global_vars.org_name)
    org.set_description(defs.global_vars.org_description)
    org.create()
    return org

def create_env(org):
    """
    Creates an environment linked to given API api
    """
    env = org.new_environment(defs.global_vars.env_name)
    env.set_description(defs.global_vars.env_description)
    env.create()
    return env

def create_host(env):
    """
    Creates a host linked to given API api
    """
    host = env.new_host(defs.global_vars.host_name)
    host.set_description(defs.global_vars.host_description)

    host.set_platform(defs.global_vars.plat_name)
    host.set_distribution(defs.global_vars.dist_name)

    for app_name in defs.global_vars.host_apps:
        host.add_application(app_name)

    for setting in defs.global_vars.host_settings:
        host.add_setting(Setting(None, setting))

    host.create()

    context = host.platform().get_single_resource()
    for setting in defs.global_vars.plat_settings:
        s = context.new_setting(setting["key"])
        s.set_value(setting["value"])
        s.create()

    return host


#==============================================================================
# Entry point
if __name__ == "__main__":
    setup.setup()
    setup.create_files()
    defs.define()
    create_resources()
