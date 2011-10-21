# control.sync - Clone system state on local filesystem and synchronize
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import os

from cortex_client.util import globals, path
from cortex_client.control.abstract import AbstractController
from cortex_client.control.exceptions import MissingException
from cortex_client.rest.exceptions import ApiException

from actions import *
from exceptions import SyncException

class SyncController(AbstractController):

    def __init__(self):
        super(SyncController, self ).__init__()
        self._register(["pull"], self._pull)
        self._register(["push"], self._push)
        self._register(["h", "help"], self._help)
        self._default_action = self._help

    def _pull(self, argv):
        self._options = globals.options
        if not self._options.username:
            raise MissingException("Pull requires a username to be defined")

        self._root = "cortex." + self._options.username

        # Ensures local repository does not contain stale data
        if(os.path.exists(self._root)):
            raise SyncException(self._root+" already exists.")

        self._ensureFolders()
        self._dumpFiles()
        self._dumpApplications()
        self._dumpDistributions()
        self._dumpOrganizations()
        self._dumpPlatforms()

    def _push(self, argv):
        """
        Pushes local data to cortex server. Data may include applications,
        distributions, platforms, organizations, environments and hosts.
        Local data are automatically pushed if no collision with remote data
        is detected. In case of collision, 'force' option can be used to still
        push data.
        """
        self._options = globals.options
        if not self._options.username:
            raise MissingException("Push requires a username")

        self._root = "cortex." + self._options.username

        self._readRemoteEntities()

        self._actions = ActionsQueue()
        self._pushFiles()
        self._pushApplications()
        self._pushDistributions()
        self._pushPlatforms()
        self._pushOrganizations()

        if(self._actions.isFastForward() or self._options.force):
            uuid_convert = UuidConversionTable()
            self._actions.executeActions(uuid_convert)
        else:
            print "Push not fast-forward:"
            self._actions.display()

    def _readRemoteEntities(self):
        file_list = self._api.get_file_collection().get_resources()
        self._remote_files = {}
        for f in file_list:
            self._remote_files[f.get_uuid()] = f

        app_list = self._api.get_application_collection().get_resources()
        self._remote_applications = {}
        for app in app_list:
            self._remote_applications[app.get_name()] = app

        dist_list = self._api.get_distribution_collection().get_resources()
        self._remote_distributions = {}
        for dist in dist_list:
            self._remote_distributions[dist.get_name()] = dist
                
        host_list = self._api.get_host_collection().get_resources()
        self._remote_hosts = {}
        for host in host_list:
            self._remote_hosts[host.get_name()] = host

        org_list = self._api.get_organization_collection().get_resources()
        self._remote_organizations = {}
        for org in org_list:
            self._remote_organizations[org.get_name()] = org

        plats_list = self._api.get_platform_collection().get_resources()
        self._remote_platforms = {}
        for plat in plats_list:
            self._remote_platforms[plat.get_name()] = plat

    def _help(self, argv):
        print """You must provide an action to perfom.

Actions:
    pull            Retrieves data from cortex server (local data are overwrit-
                    ten)
    push            Updates data on cortex server (remote data may be overwrit-
                    ten if --force option is set)
"""

    def _ensureFolders(self):
        path.ensure(os.path.join(self._root, "files"))
        path.ensure(os.path.join(self._root, "applications"))
        path.ensure(os.path.join(self._root, "distributions"))
        path.ensure(os.path.join(self._root, "organizations"))
        path.ensure(os.path.join(self._root, "platforms"))

    def _pushTemplate(self, src_folder):
        f = self._api.new_file()
        f.load(src_folder)

        local_uuid = f.get_uuid()
        if(self._remote_files.has_key(local_uuid)):
            self._actions.addAction(UpdateTemplateAction(False, f))
        else:
            self._actions.addAction(CreateTemplateAction(True, f))

    def _pushFiles(self):
        if(not os.path.exists(self._root + "/files")):
            return

        files_folder = os.path.join(self._root, "files")
        files_list = os.listdir(files_folder)
        for f in files_list:
            self._pushTemplate(os.path.join(files_folder, f))

    def _pushApplications(self):
        if(not os.path.exists(self._root + "/applications")):
            return

        app_folder = os.path.join(self._root, "applications")
        apps_list = os.listdir(app_folder)
        for app_name in apps_list:
            app = self._api.new_application()
            app.load(os.path.join(app_folder, app_name))
            self._pushResource(app, self._remote_applications)

    def _getUniqueName(self, base_name, names_dict):
        if(not names_dict.has_key(base_name)):
            return base_name

        num = 0
        new_name = base_name + str(num)
        while(names_dict.has_key(new_name)):
            num += 1
            new_name = base_name + str(num)

        return new_name

    def _pushResource(self, local_res, available_resources):
        res_name = local_res.get_name()
        local_uuid = local_res.get_uuid()
        if(available_resources.has_key(res_name)):
            remote_res = available_resources[res_name]
            remote_uuid = remote_res.get_uuid()
            if(remote_uuid == local_uuid):
                self._actions.addAction(UpdateResource(False, local_res))
            else:
                new_name = self._getUniqueName(res_name, available_resources)
                local_res.set_name(new_name)
                self._actions.addAction(CreateResource(False, local_res))
        else:
            self._actions.addAction(CreateResource(True, local_res))

    def _dumpFiles(self):
        files = self._api.get_file_collection().get_resources()
        files_folder = os.path.join(self._root, "files")
        for f in files:
            f.dump(os.path.join(files_folder, f.get_uuid()))

    def _dumpApplications(self):
        apps = self._api.get_application_collection().get_resources()
        apps_folder = os.path.join(self._root, "applications")
        for a in apps:
            app_folder = os.path.join(apps_folder, a.get_name())
            a.dump(app_folder)

    def _pushDistributions(self):
        if(not os.path.exists(self._root + "/distributions")):
            return

        dist_folder = os.path.join(self._root, "distributions")
        dists_list = os.listdir(dist_folder)
        for dist_name in dists_list:
            dist = self._api.new_distribution()
            dist.load(os.path.join(dist_folder, dist_name))
            self._pushResource(dist, self._remote_distributions)

    def _dumpDistributions(self):
        dists = self._api.get_distribution_collection().get_resources()
        dists_folder = os.path.join(self._root, "distributions")
        for d in dists:
            d.dump(os.path.join(dists_folder, d.get_name()))

    def _dumpOrganizations(self):
        orgs = self._api.get_organization_collection().get_resources()
        orgs_folder = os.path.join(self._root, "organizations")
        for o in orgs:
            org_folder = os.path.join(orgs_folder, o.get_name())
            o.dump(org_folder)

            envs = self._api.get_environment_collection().get_resources({"organizationId" : o.get_uuid()})
            for e in envs:
                env_folder = os.path.join(org_folder, e.get_name())
                e.dump(env_folder)

                hosts = self._api.get_host_collection().get_resources({"environmentId" : e.get_uuid()})
                for h in hosts:
                    h.dump(os.path.join(env_folder, h.get_name()))

    def _pushOrganizations(self):
        if(not os.path.exists(self._root + "/organizations")):
            return

        org_folder = os.path.join(self._root, "organizations")
        orgs_list = os.listdir(org_folder)
        for org in orgs_list:
            self._pushOrganization(os.path.join(org_folder, org))

    def _pushOrganization(self, org_folder):
        org = self._api.new_organization()
        org.load(org_folder)

        # Create organization
        self._pushResource(org, self._remote_organizations)

        # Get environments
        available_environments = {}
        if(org.get_uuid()):
            try:
                env_list = self._api.get_environment_collection().get_resources({"organizationId" : org.get_uuid()})
                for env in env_list:
                    available_environments[env.get_name()] = env
            except ApiException, e:
                if(e.code == 404):
                    pass
                else:
                    raise e

        # Create environments
        envs_list = os.listdir(org_folder)
        for env in envs_list:
            env_folder = os.path.join(org_folder, env)
            if(os.path.isdir(env_folder)):
                self._pushEnvironment(env_folder, available_environments)

    def _pushEnvironment(self, env_folder, available_environments):
        env = self._api.new_environment()
        env.load(env_folder)

        self._pushResource(env, available_environments)
        self._pushHosts(env_folder)

    def _pushHosts(self, env_folder):
        hosts_list = os.listdir(env_folder)
        for host in hosts_list:
            if(os.path.isdir(os.path.join(env_folder, host))):
                self._pushHost(env_folder, host)

    def _pushHost(self, env_folder, host):
        host_folder = os.path.join(env_folder, host)
        host = self._api.new_host()
        host.load(host_folder)

        # Create host
        self._pushResource(host, self._remote_hosts)

    def _dumpPlatforms(self):
        plats = self._api.get_platform_collection().get_resources()
        plats_folder = os.path.join(self._root, "platforms")
        for p in plats:
            p.dump(os.path.join(plats_folder, p.get_name()))

    def _pushPlatforms(self):
        if(not os.path.exists(self._root + "/platforms")):
            return

        plats_folder = os.path.join(self._root, "platforms")
        plats_list = os.listdir(plats_folder)
        for plat_name in plats_list:
            plat = self._api.new_platform()
            plat_folder = os.path.join(plats_folder, plat_name)
            plat.load(plat_folder)
            self._pushResource(plat, self._remote_platforms)
