# coding: utf-8

import json, os

from bisect import insort

from comodit_client.util.editor import edit_text
from comodit_client.config import Config
from comodit_client.api.settings import SimpleSetting, LinkSetting, \
    PropertySetting
from comodit_client.api.exporter import Export
from comodit_client.api.importer import Import
from comodit_client.api.sync import SyncEngine
from collections import OrderedDict


def get_names(col, params = {}):
    return [e.name for e in col.list(parameters = params)]

def get_keys(col, params = {}):
    return [e.key for e in col.list(parameters = params)]

def get_uuids(col, params = {}):
    return [e.uuid for e in col.list(parameters = params)]


class Item(object):
    def __init__(self, client, path, conts = [], leaves = []):
        self._client = client
        self._path = path
        self._conts = conts
        self._leaves = leaves
        self._details = {}

    def print_container(self, name, details = None):
        if details is None or details == '':
            print "{0: <20}".format(name + '/')
        else:
            print u"{0: <20} {1}".format(name + '/', details)

    def print_leaf(self, name, details = None):
        if details is None or details == '':
            print name
        else:
            print u"{0: <20} {1}".format(name, details)

    @property
    def absolute_path(self):
        return self._path

    @property
    def children_conts(self):
        return self._conts

    @property
    def children_leaves(self):
        return self._leaves

    @property
    def children(self):
        return self.children_conts + self.children_leaves

    def list(self, opts):
        if opts.long:
            for c in self.children_conts:
                self.print_container(c, self._details.get(c))
            for c in self.children_leaves:
                self.print_leaf(c, self._details.get(c))
        else:
            for c in self.children_conts:
                self.print_container(c)
            for c in self.children_leaves:
                self.print_leaf(c)

    def set_path_vars(self, path_vars, opts):
        pass

    def prompt(self):
        return self._path.split('/')[-1]

    def _get_entity_details(self, e):
        try:
            return e.description
        except AttributeError:
            return None

    def _add_conts(self, entities):
        for e in entities:
            self._add_cont(e.identifier, self._get_entity_details(e))

    def _add_cont(self, identifier, details = None):
        self._conts.append(identifier)
        if not details is None:
            self._details[identifier] = details

    def _add_leaves(self, entities):
        for e in entities:
            self._add_leaf(e.identifier, self._get_entity_details(e))

    def _add_leaf(self, identifier, details = None):
        self._leaves.append(identifier)
        if not details is None:
            self._details[identifier] = details


class EntityItem(Item):
    def __init__(self, client, path, conts = [], leaves = []):
        super(EntityItem, self).__init__(client, path, conts, leaves)
        self._entity = None

    def delete(self):
        self._entity.delete()

    def show(self, opts):
        self._entity.show(as_json = opts.raw)

    def update(self):
        cur_name = self._entity.name

        # Edit the entity
        original = self._entity.get_real_json(indent = 4)
        new_data = json.loads(edit_text(original), object_pairs_hook=OrderedDict)

        # Check if name has changed
        if new_data.has_key("name"):
            new_name = new_data["name"]
            if cur_name != new_name:
                self._current.rename(new_name)

        # Update entity
        self._entity.set_json(new_data)
        self._entity.update()
        self._entity.show()


class ContainerOnlyItem(Item):
    def __init__(self, client, path, conts = [], leaves = []):
        super(ContainerOnlyItem, self).__init__(client, path, conts, leaves)
        self._collection = None
        self._template = None

    def add(self, raw = False, populate = False, default = False, test = False, flavor = None):
        if self._collection == None or self._template == None:
            raise Exception("Add operation is not available in this container")

        template_json = json.load(open(os.path.join(Config()._get_templates_path(), self._template)))
        updated = edit_text(json.dumps(template_json, indent = 4))
        entity_data = json.loads(updated, object_pairs_hook=OrderedDict)

        res = self._collection._new(entity_data)

        parameters = {}
        if populate:
            parameters["populate"] = "true"
        if default:
            parameters["default"] = "true"
        if test:
            parameters["test"] = "true"
        if flavor != None:
            parameters["flavor"] = flavor

        res.create(parameters = parameters)
        res.show(as_json = raw)

    def show(self, opts):
        self.list(opts)

    def delete(self):
        self._collection.clear()


class SingleElementContainer(Item):
    def __init__(self, client, path, conts = [], leaves = []):
        super(SingleElementContainer, self).__init__(client, path, conts, leaves)
        self._collection = None
        self._template = None
        self._entity = None

    def add(self, raw = False, populate = False, default = False, test = False, flavor = None):
        if self._collection == None or self._template == None:
            raise Exception("Add operation is not available in this container")

        template_json = json.load(open(os.path.join(Config()._get_templates_path(), self._template)))
        updated = edit_text(json.dumps(template_json, indent = 4))
        entity_data = json.loads(updated, object_pairs_hook=OrderedDict)

        res = self._collection._new(entity_data)

        parameters = {}
        if populate:
            parameters["populate"] = "true"
        if default:
            parameters["default"] = "true"
        if test:
            parameters["test"] = "true"
        if flavor != None:
            parameters["flavor"] = flavor

        res.create(parameters = parameters)
        res.show(as_json = raw)

    def delete(self):
        if self._entity != None:
            self._entity.delete()

    def show(self, opts):
        if self._entity != None:
            self._entity.show(as_json = opts.raw)
        else:
            self.list(opts)

    def update(self):
        if self._entity != None:
            cur_name = self._entity.name

            # Edit the entity
            original = json.dumps(self._entity.get_json(), indent = 4)
            new_data = json.loads(edit_text(original), object_pairs_hook=OrderedDict)

            # Check if name has changed
            if new_data.has_key("name"):
                new_name = new_data["name"]
                if cur_name != new_name:
                    self._current.rename(new_name)

            # Update entity
            self._entity.set_json(new_data)
            self._entity.update()
            self._entity.show()


class RootItem(ContainerOnlyItem):
    pass


class OrganizationsItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._collection = self._client.organizations()
        self._template = 'organization.json'
        self._add_conts(self._collection)

    def import_entity(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the input folder")

        imp = Import(opts.skip_conflicts, opts.dry_run)
        imp.import_organization(self._client, opts.path)


class OrganizationItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_organization(path_vars['org_name'])

    def export(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the output folder")

        export = Export(opts.force)
        export.export_organization(self._entity, opts.path)


class GroupsItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_organization(path_vars['org_name'])
        self._add_leaves(self._parent.groups())


class GroupItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_organization(path_vars['org_name']).get_group(path_vars['group_name'])


class EnvironmentsItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_organization(path_vars['org_name'])
        self._collection = self._parent.environments()
        self._template = 'environment.json'
        self._add_conts(self._collection)

    def import_entity(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the input folder")

        imp = Import(opts.skip_conflicts, opts.dry_run)
        imp.import_environment(self._parent, opts.path)


class EnvironmentItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_environment(path_vars['org_name'], path_vars['env_name'])

    def export(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the output folder")

        export = Export(opts.force)
        export.export_environment(self._entity, opts.path)


class HostsItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_environment(path_vars['org_name'], path_vars['env_name'])
        self._collection = self._parent.hosts()
        self._template = 'host.json'
        self._add_conts(self._collection)

    def _get_entity_details(self, e):
        return u"{: <20} {: <20} {: <10}".format(e.distribution_name, e.platform_name, e.state)

    def import_entity(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the input folder")

        imp = Import(opts.skip_conflicts, opts.dry_run)
        imp.import_host(self._parent, opts.path)


class HostItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])

    def export(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the output folder")

        export = Export(opts.force)
        export.export_host(self._entity, opts.path)


class PublishablesItem(ContainerOnlyItem):
    def _get_entity_details(self, e):
        return u"{: <20}\t{}/{}/{}/{}".format(e.description, "published" if not e.published_as is None else "-", "purchased" if not e.purchased_as is None else "-", "updatable" if e.can_pull else "-", "updated" if e.can_push else "-")


class ApplicationsItem(PublishablesItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_organization(path_vars['org_name'])
        self._collection = self._parent.applications()
        self._template = 'application.json'
        self._add_conts(self._collection)

    def import_entity(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the input folder")

        imp = Import(opts.skip_conflicts, opts.dry_run)
        imp.import_application(self._parent, opts.path)


class PublishableItem(EntityItem):
    def _publish(self, store, opts):
        orgs = []
        if not opts.orgs is None:
            orgs = opts.orgs.split(',')
        store.create(self._entity.uuid, authorized_orgs = orgs)

    def _unpublish(self, store, uuid, opts):
        store.delete(uuid)

    def store_pull(self, opts):
        if self._entity.purchased_as is None:
            raise Exception("Entity was not purchased from store")

        pur = self._get_purchased(self._entity.purchased_as)
        pur.update()

    def store_push(self, opts):
        if self._entity.published_as is None:
            raise Exception("Entity was not published into the store")

        pub = self._get_published(self._entity.published_as)
        pub.update()


class SyncableItem(EntityItem):
    def sync_pull(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the local folder")

        sync = SyncEngine(opts.path)
        sync.pull(self._entity, opts.dry_run)

    def sync_push(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the local folder")

        sync = SyncEngine(opts.path)
        sync.push(self._entity, opts.dry_run)


class ApplicationItem(PublishableItem, SyncableItem):
    def set_path_vars(self, path_vars, opts):
        self._org = self._client.get_organization(path_vars['org_name'])
        self._entity = self._org.get_application(path_vars['app_name'])

    def publish(self, opts):
        self._publish(self._client.app_store(), opts)

    def unpublish(self, opts):
        self._unpublish(self._client.app_store(), self._entity.published_as, opts)

    def _get_purchased(self, uuid):
        return self._org.get_purchased_app(uuid)

    def _get_published(self, uuid):
        return self._client.get_published_app(uuid, self._org.name)

    def export(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the output folder")

        export = Export(opts.force)
        export.export_application(self._entity, opts.path)


class DistributionsItem(PublishablesItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_organization(path_vars['org_name'])
        self._collection = self._parent.distributions()
        self._template = 'distribution.json'
        self._add_conts(self._collection)

    def import_entity(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the input folder")

        imp = Import(opts.skip_conflicts, opts.dry_run)
        imp.import_distribution(self._parent, opts.path)


class DistributionItem(PublishableItem, SyncableItem):
    def set_path_vars(self, path_vars, opts):
        self._org = self._client.get_organization(path_vars['org_name'])
        self._entity = self._org.get_distribution(path_vars['dist_name'])

    def publish(self, opts):
        self._publish(self._client.dist_store(), opts)

    def unpublish(self, opts):
        self._unpublish(self._client.dist_store(), self._entity.published_as, opts)

    def _get_purchased(self, uuid):
        return self._org.get_purchased_dist(uuid)

    def _get_published(self, uuid):
        return self._client.get_published_dist(uuid, self._org.name)

    def export(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the output folder")

        export = Export(opts.force)
        export.export_distribution(self._entity, opts.path)


class PlatformsItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_organization(path_vars['org_name'])
        self._collection = self._parent.platforms()
        self._template = 'platform.json'
        self._add_conts(self._collection)

    def import_entity(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the input folder")

        imp = Import(opts.skip_conflicts, opts.dry_run)
        imp.import_platform(self._parent, opts.path)


class PlatformItem(SyncableItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_platform(path_vars['org_name'], path_vars['plat_name'])

    def export(self, opts):
        if opts.path is None:
            raise Exception("You must provide the path to the output folder")

        export = Export(opts.force)
        export.export_platform(self._entity, opts.path)


class HostAppsItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._collection = self._parent.applications()
        self._template = 'application_context.json'
        self._add_conts(self._collection)


class HostAppItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_application(path_vars['app_name'])


class HostDistItem(SingleElementContainer):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._collection = self._parent.distribution()
        self._template = 'distribution_context.json'
        try:
            self._entity = self._collection.get()
        except:
            pass


class HostPlatItem(SingleElementContainer):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._collection = self._parent.platform()
        self._template = 'platform_context.json'
        try:
            self._entity = self._collection.get()
        except:
            pass


class HostInstanceItem(SingleElementContainer):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._collection = self._parent.instance()
        try:
            self._entity = self._collection.get()
        except:
            pass

    def add(self, raw = False, populate = False, default = False, test = False, flavor = None):
        self._collection.create()

    def _ensure_instance(self):
        if self._entity == None:
            raise Exception("Host must have an instance")

    def show_content(self, path = None):
        self._ensure_instance()
        print self._entity.get_file_content(path).read(),

    def start(self):
        self._ensure_instance()
        self._entity.start()

    def pause(self):
        self._ensure_instance()
        self._entity.start()

    def resume(self):
        self._ensure_instance()
        self._entity.start()

    def shutdown(self):
        self._ensure_instance()
        self._entity.start()

    def poweroff(self):
        self._ensure_instance()
        self._entity.start()

    def show_properties(self):
        self._ensure_instance()
        for p in self._entity.properties:
            p.show()


class HostChangesItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        for c in self._parent.changes().list(show_processed = True):
            self._leaves.append(c.name)


class HostChangeItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._entity = host.get_change(path_vars['task_num'])


class RootCompliancesItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._parent = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._collection = self._parent.compliance()
        apps = set()
        for e in self._collection:
            apps.add(e.application)
        self._conts += apps


class HostAppCompliancesItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._app = path_vars['app_name']
        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        cols = set()
        for e in host.compliance():
            cols.add(e.type_collection)
        self._conts += cols


class CompliancesItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        self._app = path_vars['app_name']
        self._col = path_vars['col_type']
        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        ids = set()
        for e in host.compliance():
            if e.application == self._app and e.type_collection == self._col:
                ids.add(e.res_name)
        self._leaves += ids


class ComplianceItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._app = path_vars['app_name']
        self._col = path_vars['col_type']
        self._id = path_vars['comp_id']

        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._entity = host.get_compliance_error('applications/' + self._app + '/' + self._col + '/' + self._id)


# Settings

class SettingsItem(ContainerOnlyItem):

    def _set_parent(self, parent):
        self._parent = parent
        self._collection = self._parent.settings()
        self._template = 'setting.json'
        self._add_leaves(self._collection)

    def _get_entity_details(self, e):
        if isinstance(e, SimpleSetting):
            return "{: <60}".format(e.value)
        elif isinstance(e, LinkSetting):
            return "{: <20} {: <40}".format(e.link, e.value)
        elif isinstance(e, PropertySetting):
            return "{: <60}".format(e.property_f)


class OrgSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_organization(path_vars['org_name']))


class OrgSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_organization(path_vars['org_name']).get_setting(path_vars['key'])


class EnvSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_environment(path_vars['org_name'], path_vars['env_name']))


class EnvSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_environment(path_vars['org_name'], path_vars['env_name']).get_setting(path_vars['key'])


class HostSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']))


class HostSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_setting(path_vars['key'])


class DistSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_distribution(path_vars['org_name'], path_vars['dist_name']))


class DistSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_distribution(path_vars['org_name'], path_vars['dist_name']).get_setting(path_vars['key'])


class PlatSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_platform(path_vars['org_name'], path_vars['plat_name']))


class PlatSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_platform(path_vars['org_name'], path_vars['plat_name']).get_setting(path_vars['key'])


class HostAppSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_application(path_vars['app_name']))


class HostAppSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_application(path_vars['app_name']).get_setting(path_vars['key'])


class HostDistSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_distribution())


class HostDistSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_distribution().get_setting(path_vars['key'])


class HostPlatSettingsItem(SettingsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_platform())


class HostPlatSettingItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name']).get_platform().get_setting(path_vars['key'])


# Parameters

class ParamsItem(ContainerOnlyItem):

    def _set_parent(self, parent):
        self._parent = parent
        self._collection = self._parent.parameters()
        self._template = 'parameter.json'
        self._add_leaves(self._collection)

    def _get_entity_details(self, e):
        return u"{: <30} {: <20} {: <10}".format(e.description, e.key, e.value)


class AppParamsItem(ParamsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_application(path_vars['org_name'], path_vars['app_name']))


class AppParamItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_application(path_vars['org_name'], path_vars['app_name']).get_parameter(path_vars['param_name'])


class DistParamsItem(ParamsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_distribution(path_vars['org_name'], path_vars['dist_name']))


class DistParamItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_distribution(path_vars['org_name'], path_vars['dist_name']).get_parameter(path_vars['param_name'])


class PlatParamsItem(ParamsItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_platform(path_vars['org_name'], path_vars['plat_name']))


class PlatParamItem(EntityItem):
    def set_path_vars(self, path_vars, opts):
        self._entity = self._client.get_platform(path_vars['org_name'], path_vars['plat_name']).get_parameter(path_vars['param_name'])


# Files

class FilesItem(ContainerOnlyItem):

    def _set_parent(self, parent):
        self._parent = parent
        self._collection = self._parent.files()
        self._template = 'file.json'
        self._leaves += get_names(self._collection)


class FileItem(EntityItem):

    def _set_file(self, parent, name):
        self._parent = parent
        self._entity = self._parent.get_file(name)

    def show_content(self, path = None):
        print self._entity.get_content().read()

    def set_content(self, path):
        print self._entity.set_content(path)


class AppFilesItem(FilesItem):

    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_application(path_vars['org_name'], path_vars['app_name']))
        self._template = 'application_file.json'


class AppFileItem(FileItem):
    def set_path_vars(self, path_vars, opts):
        self._set_file(self._client.get_application(path_vars['org_name'], path_vars['app_name']), path_vars['file_name'])


class DistFilesItem(FilesItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_distribution(path_vars['org_name'], path_vars['dist_name']))


class DistFileItem(FileItem):
    def set_path_vars(self, path_vars, opts):
        self._set_file(self._client.get_distribution(path_vars['org_name'], path_vars['dist_name']), path_vars['file_name'])


class PlatFilesItem(FilesItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_platform(path_vars['org_name'], path_vars['plat_name']))


class PlatFileItem(FileItem):
    def set_path_vars(self, path_vars, opts):
        self._set_file(self._client.get_platform(path_vars['org_name'], path_vars['plat_name']), path_vars['file_name'])


# File rendering

class RenderedFilesItem(ContainerOnlyItem):
    def _set_parent(self, parent):
        self._parent = parent
        self._leaves += get_names(parent.files())

    def add(self, raw = False, populate = False, default = False, test = False, flavor = None):
        raise NotImplementedError()


class RenderedFileItem(Item):
    def _set_host(self, path_vars):
        self._host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])


class HostAppFilesItem(RenderedFilesItem):
    def set_path_vars(self, path_vars, opts):
        self._set_parent(self._client.get_application(path_vars['org_name'], path_vars['app_name']))


class HostAppFileItem(RenderedFileItem):
    def set_path_vars(self, path_vars, opts):
        self._set_host(path_vars)
        self._app = path_vars['app_name']
        self._file = path_vars['file_name']

    def show_content(self, path = None):
        print self._host.render_app_file(self._app, self._file).read()

    def live_update(self, opts):
        self._host.live_update_file(self._app, self._file)


class HostAppPackagesItem(Item):
    def set_path_vars(self, path_vars, opts):
        app = self._client.get_application(path_vars['org_name'], path_vars['app_name'])
        for p in app.packages:
            self._add_leaf(p.name)


class HostAppPackageItem(Item):
    def set_path_vars(self, path_vars, opts):
        self._host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._app = path_vars['app_name']
        self._pkg = path_vars['pkg_name']

    def live_install(self, opts):
        self._host.live_install_package(self._app, self._pkg)


class HostAppServicesItem(ContainerOnlyItem):
    def set_path_vars(self, path_vars, opts):
        app = self._client.get_application(path_vars['org_name'], path_vars['app_name'])
        for s in app.services:
            self._add_leaf(s.name)


class HostAppServiceItem(Item):
    def set_path_vars(self, path_vars, opts):
        self._host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._app = path_vars['app_name']
        self._svc = path_vars['svc_name']

    def live_restart(self, opts):
        self._host.live_restart_service(self._app, self._svc)


class HostDistFilesItem(RenderedFilesItem):
    def set_path_vars(self, path_vars, opts):
        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        dist = host.get_distribution().distribution
        self._set_parent(self._client.get_distribution(path_vars['org_name'], dist))


class HostDistFileItem(RenderedFileItem):
    def set_path_vars(self, path_vars, opts):
        self._set_host(path_vars)
        self._file = path_vars['file_name']

    def show_content(self, path = None):
        print self._host.render_dist_file(self._file).read()


class HostPlatFilesItem(RenderedFilesItem):
    def set_path_vars(self, path_vars, opts):
        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        plat = host.get_platform().platform
        self._set_parent(self._client.get_platform(path_vars['org_name'], plat))


class HostPlatFileItem(RenderedFileItem):
    def set_path_vars(self, path_vars, opts):
        self._set_host(path_vars)
        self._file = path_vars['file_name']

    def show_content(self, path = None):
        print self._host.render_plat_file(self._file).read()


# Audit

class Audits(ContainerOnlyItem):
    def _set_parent(self, parent):
        self._collection = parent.audit_logs()
        for log in self._collection:
            user = log.initiator_full_name
            if user is None or user == "":
                user = log.initiator_username
            self._leaves.append('{0} {1} by {2}'.format(log.timestamp, log.message, user))


class OrgAudits(Audits):
    def set_path_vars(self, path_vars, opts):
        org = self._client.get_organization(path_vars['org_name'])
        self._set_parent(org)


class EnvAudits(Audits):
    def set_path_vars(self, path_vars, opts):
        env = self._client.get_environment(path_vars['org_name'], path_vars['env_name'])
        self._set_parent(env)


class HostAudits(Audits):
    def set_path_vars(self, path_vars, opts):
        host = self._client.get_host(path_vars['org_name'], path_vars['env_name'], path_vars['host_name'])
        self._set_parent(host)


# Stores

class StoreItem(ContainerOnlyItem):
    def _set_collection(self, col):
        self._collection = col
        for e in col:
            self._add_leaf(e.uuid, e.name)

    def list(self, opts):
        if opts.filter is None and opts.org is None:
            super(StoreItem, self).list(opts)
        else:
            # Use provided organization name and filter
            params = {}
            if opts.filter != None:
                params["filter"] = opts.filter
            if opts.org != None:
                params["org_name"] = opts.org

            for e in self._collection.list(parameters = params):
                if opts.long:
                    self.print_leaf(e.uuid, e.name)
                else:
                    self.print_leaf(e.uuid)


class AppStoreItem(StoreItem):
    def set_path_vars(self, path_vars, opts):
        self._set_collection(self._client.app_store())


class PubItem(EntityItem):
    def _purchase(self, opts):
        if opts.org is None:
            raise Exception("No target organizations provided")

        if opts.name is None:
            name = self._entity.name
        else:
            name = opts.name

        col = self._get_purchased_col(opts.org)
        col.create(self._entity.uuid, name)


class PubAppItem(PubItem):
    def set_path_vars(self, path_vars, opts):
        if opts.org is None:
            self._entity = self._client.get_published_app(path_vars['pub_uuid'])
        else:
            self._entity = self._client.get_published_app(path_vars['pub_uuid'], org_name = opts.org)

    def _get_purchased_col(self, org_name):
        return self._client.get_organization(org_name).purchased_apps()

    def purchase(self, opts):
        self._purchase(opts)


class DistStoreItem(StoreItem):
    def set_path_vars(self, path_vars, opts):
        self._set_collection(self._client.dist_store())


class PubDistItem(PubItem):
    def set_path_vars(self, path_vars, opts):
        if opts.org is None:
            self._entity = self._client.get_published_dist(path_vars['pub_uuid'])
        else:
            self._entity = self._client.get_published_dist(path_vars['pub_uuid'], org_name = opts.org)

    def _get_purchased_col(self, org_name):
        return self._client.get_organization(org_name).purchased_dists()

    def purchase(self, opts):
        self._purchase(opts)
