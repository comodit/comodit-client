#==============================================================================
# This file illustrates the use of Python API to handle cortex entities.
# Definitions section (after imports) provides the description of several
# entities this script will create (it may need to be updated).
# Script section (after definitions) contains the actual operations (entities
# creation, host provisioning, shutdown and entities removal).
#==============================================================================

# Setup Python path
import sys
sys.path.append("..")


#==============================================================================
# Imports section

import time

from cortex_client.api.api import CortexApi
from cortex_client.api.exceptions import PythonApiException
from cortex_client.api.collection import ResourceNotFoundException
from cortex_client.api.application import Package
from cortex_client.api.host import Setting
from cortex_client.api.file import Parameter


#==============================================================================
# Definitions section

# Define application
app_name = "htop2"
app_packages = ["htop"]
app_description = "Htop Application"

# Define platform
plat_name = "Local2"
plat_description = "Local QEMU"
plat_driver = "com.guardis.cortex.server.services.provisioning.LibvirtDriver"
plat_settings = [{"key":"libvirt.connectUrl",
                 "value":"qemu:///system"}]

# Define distribution (kickstart template is in same folder)
dist_name = "co6i686"
dist_description = "CentOS 6 i686"
dist_url = "http://oak.angleur.guardis.be/public/centos/6.0/os/i386/"
dist_initrd = "/var/lib/libvirt/boot/initrd.img.centos.6.i386"
dist_vmlinuz = "/var/lib/libvirt/boot/vmlinuz.centos.6.i386"

dist_kickstart = "co6.ks"
dist_kickstart_params = [{"key": "zone", "value":"angleur"},
                         {"key": "vm_arch", "value":"i686"},
                         {"key": "vm_base_arch", "value":"i386"},
                         {"key": "enable_trunk", "value":"true"},
                         {"key": "ks_rootpw_one", "value":"secret"}]

# Define organization and environment(s)
org_name = "Guardis2"
org_description = "Guardis2's organization"
org_envs= [{"name": "Test2", "description":"Test environment 1 of Guardis2"},
           {"name": "Test3", "description":"Test environment 2 of Guardis2"}]

# Define host
host_name = "test2"
host_description = "Single host of Test2 environment"
host_env = "Guardis2/Test2"
host_dist = dist_name
host_plat = plat_name
host_apps = [app_name]
host_settings = [{"key":"vm_arch", "value":"i686"},
                 {"key":"vm_bridge", "value":"br0"},
                 {"key":"vm_memory", "value":"1024"},
                 {"key":"vm_capacity", "value":"3072"},
                 {"key":"vm_nvirtcpus", "value":"1"}]


#==============================================================================
# Script

def main():
    # API from server cortex listening on port 8000 of localhost is used
    # Username "admin" and password "secret" are used for authentification
    api = CortexApi("http://localhost:8000/api", "admin", "secret")


    ##################################################################
    # Create entities (if they do not already exist) described above #
    ##################################################################

    print "="*80
    print "Application"
    app_coll = api.get_application_collection()
    try:
        app = app_coll.get_resource_from_path(app_name)
        print "Application already exists"
    except ResourceNotFoundException:
        app = create_app(api)
        print "Application is created"
    app.show()

    print "="*80
    print "Platform"
    plat_coll = api.get_platform_collection()
    try:
        plat = plat_coll.get_resource_from_path(plat_name)
        print "Platform already exists"
    except ResourceNotFoundException:
        plat = create_plat(api)
        print "Platform is created"
    plat.show()

    print "="*80
    print "Distribution"
    dist_coll = api.get_distribution_collection()
    try:
        dist = dist_coll.get_resource_from_path(dist_name)
        print "Distribution already exists"
    except ResourceNotFoundException:
        dist = create_dist(api)
        print "Distribution is created"
    dist.show()

    print "="*80
    print "Organization"
    org_coll = api.get_organization_collection()
    try:
        org = org_coll.get_resource_from_path(org_name)
        print "Organization already exists"
    except ResourceNotFoundException:
        org = create_org(api)
        print "Organization is created"
    org.show()

    print "="*80
    print "Environments"
    env_coll = api.get_environment_collection()
    envs = []
    for env_desc in org_envs:
        env_name = env_desc["name"]
        try:
            env = env_coll.get_resource_from_path(org_name + "/" + env_name)
            print "Environment " + env_name + " already exists"
        except ResourceNotFoundException:
            env = create_env(api, env_desc, org)
            print "Environment " + env_name + " is created"
        envs.append(env)
        env.show()

    print "="*80
    print "Host"
    host_coll = api.get_host_collection()
    try:
        host = host_coll.get_resource_from_path(host_env + "/" + host_name)
        print "Host already exists"
    except ResourceNotFoundException:
        host = create_host(api, host_env)
        print "Host is created"
    host.show()


    ####################################
    # Provision and then poweroff host #
    ####################################

    print "="*80
    print "Provisioning host "+host_name
    try:
        host.provision()
    except PythonApiException, e:
        print e.message
        print e.cause.code
        print e.cause.message

    print "="*80
    print "Waiting 3 seconds..."
    time.sleep(3)

    print "="*80
    print "Poweroff host"
    try:
        host.poweroff()
    except Exception, e:
        print e.message


    ###################
    # Delete entities #
    ###################

    print "="*80
    print "Delete host (and VM)"
    try:
        host.delete(delete_vm=True)
    except Exception, e:
        print e.message

    print "="*80
    print "Delete application"
    try:
        app.delete()
    except Exception, e:
        print e.message

    print "="*80
    print "Delete platform"
    try:
        plat.delete()
    except Exception, e:
        print e.message

    print "="*80
    print "Delete distribution"
    try:
        dist.delete()
    except Exception, e:
        print e.message

    print "="*80
    print "Delete environments"
    for e in envs:
        try:
            e.delete()
        except Exception, e:
            print e.message

    print "="*80
    print "Delete organization"
    try:
        org.delete()
    except Exception, e:
        print e.message


def create_app(api):
    """
    Creates an application linked to given API api
    """
    app = api.new_application()
    app.set_name(app_name)
    app.set_description(app_description)

    for p in app_packages:
        app_pck = Package()
        app_pck.set_name(p)
        app.add_package(app_pck)

    app.create()
    return app

def create_plat(api):
    """
    Creates a platform linked to given API api
    """
    plat = api.new_platform()
    plat.set_name(plat_name)
    plat.set_description(plat_description)
    plat.set_driver(plat_driver)

    for s in plat_settings:
        plat.add_setting(Setting(s))

    plat.create()
    return plat

def create_dist(api):
    """
    Creates a distribution linked to given API api
    """
    dist = api.new_distribution()
    dist.set_name(dist_name)
    dist.set_description(dist_description)
    dist.set_url(dist_url)
    dist.set_initrd(dist_initrd)
    dist.set_vmlinuz(dist_vmlinuz)

    # Create kickstart template
    kickstart_file = api.new_file()
    kickstart_file.set_name(dist_name + " kickstart")
    kickstart_file.set_content(dist_kickstart)
    for p in dist_kickstart_params:
        kickstart_file.add_parameter(Parameter(p))
    kickstart_file.create()

    dist.set_kickstart(kickstart_file.get_uuid())
    dist.create()

    return dist

def create_org(api):
    """
    Creates an organization linked to given API api
    """
    org = api.new_organization()
    org.set_name(org_name)
    org.set_description(org_description)
    org.create()
    return org

def create_env(api, env_desc, org):
    """
    Creates an environment linked to given API api
    """
    env = api.new_environment()
    env.set_name(env_desc["name"])
    env.set_description(env_desc["description"])
    env.set_organization(org.get_uuid())
    env.create()
    return env

def create_host(api, env_path):
    """
    Creates a host linked to given API api
    """
    host = api.new_host()
    host.set_name(host_name)
    host.set_description(host_description)

    env = api.get_environment_collection().get_resource_from_path(env_path)
    host.set_environment(env.get_uuid())
    
    plat = api.get_platform_collection().get_resource_from_path(host_plat)
    host.set_platform(plat.get_uuid())

    dist = api.get_distribution_collection().get_resource_from_path(host_dist)
    host.set_distribution(dist.get_uuid())

    for app_name in host_apps:
        app = api.get_application_collection().get_resource_from_path(app_name)
        host.add_application(app.get_uuid())

    for setting in host_settings:
        host.add_setting(Setting(setting))

    host.create()
    return host


#==============================================================================
# Entry point
if __name__ == "__main__":
    main()
