# control.sync - Clone system state on local filesystem and synchronize
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import os, json, shutil

from cortex_client.util import globals, path
from cortex_client.control.abstract import AbstractController
from cortex_client.control.exceptions import MissingException
from cortex_client.control.exceptions import ControllerException
from cortex_client.rest.client import Client
from cortex_client.rest.exceptions import ApiException
from actions import *

class SyncException(ControllerException):
    def __init__(self, msg):
        ControllerException.__init__(self, msg)

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

        self._client = Client(self._options.api, self._options.username, self._options.password)
        self._root = "cortex." + self._options.username

        # Ensures local repository does not contain stale data
        if(os.path.exists(self._root)):
            shutil.rmtree(self._root)

        self._ensureFolders()
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

        self._client = Client(self._options.api, self._options.username, self._options.password)
        self._root = "cortex." + self._options.username

        self._readRemoteEntities()

        self._actions = ActionsQueue()
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

    def _readDefinitionFile(self, file_name):
        if(not os.path.exists(file_name)):
            raise SyncException("Definition file "+file_name+" not found")
    
        with open(file_name, 'r') as f:
            return json.load(f)

    def _readRemoteEntities(self):
        file_list = self._client.read("files")
        self._remote_files = {}
        if(file_list["count"] != "0"):
            for f in file_list["items"]:
                self._remote_files[f["uuid"]] = f

        app_list = self._client.read("applications")
        self._remote_applications = {}
        if(app_list["count"] != "0"):
            for app in app_list["items"]:
                self._remote_applications[app["name"]] = app
        
        dist_list = self._client.read("distributions")
        self._remote_distributions = {}
        if(dist_list["count"] != "0"):
            for dist in dist_list["items"]:
                self._remote_distributions[dist["name"]] = dist
                
        host_list = self._client.read("hosts")
        self._remote_hosts = {}
        if(host_list["count"] != "0"):
            for host in host_list["items"]:
                self._remote_hosts[host["name"]] = host

        org_list = self._client.read("organizations")
        self._remote_organizations = {}
        if(org_list["count"] != "0"):
            for org in org_list["items"]:
                self._remote_organizations[org["name"]] = org

        plats_list = self._client.read("platforms")
        self._remote_platforms = {}
        if(plats_list["count"] != "0"):
            for plat in plats_list["items"]:
                self._remote_platforms[plat["name"]] = plat

    def _help(self, argv):
        print """You must provide an action to perfom.

Actions:
    pull            Retrieves data from cortex server (local data are overwrit-
                    ten)
    push            Updates data on cortex server (remote data may be overwrit-
                    ten if --force option is set)
"""

    def _ensureFolders(self):
        path.ensure(os.path.join(self._root, "applications"))
        path.ensure(os.path.join(self._root, "distributions"))
        path.ensure(os.path.join(self._root, "organizations"))
        path.ensure(os.path.join(self._root, "platforms"))

    def _dumpTemplate(self, dest_folder, file_uuid, template_folder_name = None):
        """
        Dumps a template to a given folder. A template includes a file as well
        as parameters associated to it. This method creates a subfolder whose name
        is the file UUID or is given as argument. This subfolder will contain
        2 files: the template file as well as a JSON file (definition.json)
        containing associated parameters.
        """
        path.ensure(dest_folder)
        content = self._client.read('files/' + file_uuid, decode=False)
        file_meta = self._client.read('files/' + file_uuid + '/_meta')
        file_name = file_meta['name']
        if(template_folder_name != None):
            output_folder = os.path.join(dest_folder, template_folder_name)
        else:
            output_folder = os.path.join(dest_folder, file_uuid)
        path.ensure(output_folder)
        with open(os.path.join(output_folder, file_name), 'w') as f:
            f.write(content.read())
        with open(os.path.join(output_folder, "definition.json"), 'w') as f:
            f.write(json.dumps(file_meta, sort_keys=True, indent=4))

    def _pushTemplate(self, root_folder, template_subfolder):
        src_folder = os.path.join(root_folder, template_subfolder)
        if(not os.path.exists(src_folder)):
            raise SyncException("Template folder does not exist")
        with open(os.path.join(src_folder, "definition.json"), 'r') as f:
            template_meta = json.load(f)

        local_uuid = template_meta["uuid"]
        if(self._remote_files.has_key(local_uuid)):
            self._actions.addAction(UpdateTemplateAction(False, self._client, src_folder, template_meta))
        else:
            self._actions.addAction(CreateTemplateAction(True, self._client, src_folder, template_meta))

    def _pushApplications(self):
        if(not os.path.exists(self._root + "/applications")):
            return

        app_folder = os.path.join(self._root, "applications")
        apps_list = os.listdir(app_folder)
        self._new_from_old_app = {}
        for app in apps_list:
            self._pushApplication(os.path.join(app_folder, app))

    def _getUniqueName(self, base_name, names_dict):
        if(not names_dict.has_key(base_name)):
            return base_name

        num = 0
        new_name = base_name + str(num)
        while(names_dict.has_key(new_name)):
            num += 1
            new_name = base_name + str(num)

        return new_name

    def _pushResource(self, res_type, local_res, available_resources):
        res_name = local_res["name"]
        local_uuid = local_res["uuid"]
        if(available_resources.has_key(res_name)):
            remote_res = available_resources[res_name]
            remote_uuid = remote_res["uuid"]
            if(remote_uuid == local_uuid):
                self._actions.addAction(UpdateResource(False, self._client,
                                                       res_type, local_res))
            else:
                new_name = self._getUniqueName(res_name, available_resources)
                local_res["name"] = new_name
                self._actions.addAction(CreateResource(False, self._client,
                                                       res_type, local_res))
        else:
            self._actions.addAction(CreateResource(True, self._client,
                                                       res_type, local_res))

    def _pushApplication(self, app_folder):
        def_file = os.path.join(app_folder, "definition.json")
        app_def = self._readDefinitionFile(def_file)

        # Upload file resources
        app_files = app_def["files"]
        for app_file in app_files:
            template_uuid = app_file["template"]
            self._pushTemplate(app_folder, template_uuid)

        # Define new application
        self._pushResource("applications", app_def, self._remote_applications)

    def _dumpApplications(self):
        result = self._client.read('applications')
        if not (result['count'] == "0"):
            for o in result['items']:
                name = o['name']
                output_dir = os.path.join(self._root, "applications", name)
                path.ensure(output_dir)
                app_meta = json.dumps(o, sort_keys=True, indent=4)
                with open(os.path.join(output_dir, "definition.json"), 'w') as f:
                    f.write(app_meta)
                for t in o["files"]:
                    file_uuid = t["template"]
                    self._dumpTemplate(output_dir, file_uuid)

    def _pushDistributions(self):
        if(not os.path.exists(self._root + "/distributions")):
            return

        dist_folder = os.path.join(self._root, "distributions")
        dists_list = os.listdir(dist_folder)
        self._new_from_old_dist = {}
        for dist in dists_list:
            self._pushDistribution(os.path.join(dist_folder, dist))

    def _pushDistribution(self, dist_folder):
        def_file = os.path.join(dist_folder, "definition.json")
        dist_def = self._readDefinitionFile(def_file)

        # Upload kickstart
        self._pushTemplate(dist_folder, "kickstart")

        # Define new distribution
        self._pushResource("distributions", dist_def, self._remote_distributions)

    def _dumpDistributions(self):
        result = self._client.read('distributions')
        if not (result['count'] == "0"):
            for o in result['items']:
                # Dump distribution description
                dist_name = o['name']
                data = json.dumps(o, sort_keys=True, indent=4)
                dist_folder = os.path.join(self._root, "distributions", dist_name)
                path.ensure(dist_folder)
                with open(os.path.join(dist_folder, "definition.json"), 'w') as f:
                    f.write(data)

                # Dump kickstart
                ks_uuid = o['kickstart']
                self._dumpTemplate(dist_folder, ks_uuid, "kickstart")

    def _dumpOrganizations(self):
        result = self._client.read('organizations')
        if not (result['count'] == "0"):
            for o in result['items']:
                data = json.dumps(o, sort_keys=True, indent=4)
                uuid = o['uuid']
                name = o['name']
                file = os.path.join(self._root, "organizations", name)
                path.ensure(file)
                with open(os.path.join(file, "definition.json"), 'w') as f:
                    f.write(data)
                self._dumpEnvironments(uuid, file)

    def _pushOrganizations(self):
        if(not os.path.exists(self._root + "/organizations")):
            return

        org_folder = os.path.join(self._root, "organizations")
        orgs_list = os.listdir(org_folder)
        for org in orgs_list:
            self._pushOrganization(os.path.join(org_folder, org))

    def _pushOrganization(self, org_folder):
        def_file = os.path.join(org_folder, "definition.json")
        org_def = self._readDefinitionFile(def_file)

        # Create organization
        self._pushResource("organizations", org_def, self._remote_organizations)

        # Get environments
        available_environments = {}
        if(org_def.has_key("uuid")):
            try:
                env_list = self._client.read("environments",
                                             {"organizationId" : org_def["uuid"]})
                if(env_list["count"] != "0"):
                    for env in env_list["items"]:
                        available_environments[env["name"]] = env
            except ApiException, e:
                if(e.code == 404):
                    pass
                else:
                    raise e

        # Create environments
        envs_list = os.listdir(org_folder)
        for env in envs_list:
            if(os.path.isdir(os.path.join(org_folder, env))):
                self._pushEnvironment(org_folder, env, available_environments)

    def _pushEnvironment(self, org_folder, env_name, available_environments):
        env_folder = os.path.join(org_folder, env_name)
        def_file = os.path.join(env_folder, "definition.json")
        env_def = self._readDefinitionFile(def_file)

        self._pushResource("environments", env_def, available_environments)
        self._pushHosts(env_folder)

    def _pushHosts(self, env_folder):
        hosts_list = os.listdir(env_folder)
        for host in hosts_list:
            if(os.path.isdir(os.path.join(env_folder, host))):
                self._pushHost(env_folder, host)

    def _pushHost(self, env_folder, host):
        host_folder = os.path.join(env_folder, host)
        def_file = os.path.join(host_folder, "definition.json")
        host_def = self._readDefinitionFile(def_file)

        # Create host
        self._pushResource("hosts", host_def, self._remote_hosts)

    def _dumpEnvironments(self, uuid, root):
        result = self._client.read('environments', parameters={"organizationId":uuid})
        if not (result['count'] == "0"):
            for o in result['items']:
                data = json.dumps(o, sort_keys=True, indent=4)
                uuid = o['uuid']
                name = o['name']
                file = os.path.join(root, name)
                path.ensure(file)
                with open(os.path.join(file, "definition.json"), 'w') as f:
                    f.write(data)
                self._dumpHosts(uuid, file)

    def _dumpHosts(self, uuid, root):
        result = self._client.read('hosts', parameters={"environmentId":uuid})
        if not (result['count'] == "0"):
            for o in result['items']:
                data = json.dumps(o, sort_keys=True, indent=4)
                uuid = o['uuid']
                name = o['name']
                file = os.path.join(root, name)
                path.ensure(file)
                with open(os.path.join(file, "definition.json"), 'w') as f:
                    f.write(data)

    def _dumpPlatforms(self):
        result = self._client.read('platforms')
        if not (result['count'] == "0"):
            for o in result['items']:
                data = json.dumps(o, sort_keys=True, indent=4)
                uuid = o['uuid']
                name = o['name']
                file = os.path.join(self._root, "platforms")
                path.ensure(file)
                with open(os.path.join(file, name + ".json"), 'w') as f:
                    f.write(data)
                    
    def _pushPlatforms(self):
        if(not os.path.exists(self._root + "/platforms")):
            return

        plat_folder = os.path.join(self._root, "platforms")
        plats_list = os.listdir(plat_folder)
        self._new_from_old_plat = {}
        for plat_file_name in plats_list:
            self._pushPlatform(plat_folder, plat_file_name)

    def _pushPlatform(self, plat_folder, plat_file_name):
        def_file = os.path.join(plat_folder, plat_file_name)
        plat_def = self._readDefinitionFile(def_file)

        self._pushResource("platforms", plat_def, self._remote_platforms)
