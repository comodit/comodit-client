from exceptions import SyncException

from cortex_client.api.application import Application
from cortex_client.api.distribution import Distribution
from cortex_client.api.organization import Organization
from cortex_client.api.environment import Environment
from cortex_client.api.host import Host
from cortex_client.api.platform import Platform

class UuidConversionTable:
    def __init__(self):
        self._new_from_old = {}

    def putUuidPair(self, old_uuid, new_uuid):
        self._new_from_old[old_uuid] = new_uuid

    def getNewUuid(self, old_uuid):
        return self._new_from_old[old_uuid]

class Action(object):
    def __init__(self, is_fast_forward):
        self._is_fast_forward = is_fast_forward

    def isFastForward(self):
        return self._is_fast_forward

    def executeAction(self, uuid_conversion_table):
        raise NotImplementedError

    def display(self):
        print "Fast-forward:", self._is_fast_forward

class TemplateAction(Action):
    def __init__(self, is_fast_forward, file_object):
        super(TemplateAction, self).__init__(is_fast_forward)
        self._file_object = file_object

class UpdateTemplateAction(TemplateAction):
    def __init__(self, is_fast_forward, file_object):
        super(UpdateTemplateAction, self).__init__(is_fast_forward, file_object)

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._file_object.get_uuid()
        self._file_object.commit()
        new_uuid = self._file_object.get_uuid()
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(UpdateTemplateAction, self).display()
        print "Summary: Update template " + self._file_object.get_name()

class CreateTemplateAction(TemplateAction):
    def __init__(self, is_fast_forward, file_object):
        super(CreateTemplateAction, self).__init__(is_fast_forward, file_object)

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._file_object.get_uuid()
        self._file_object.create()
        new_uuid = self._file_object.get_uuid()
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(CreateTemplateAction, self).display()
        print "Summary: Create template " + self._file_object.get_name()

class ResourceAction(Action):
    def __init__(self, is_fast_forward, res_object):
        super(ResourceAction, self).__init__(is_fast_forward)
        self._res_object = res_object

    def _update_meta_data(self, uuid_conversion_table):
        if(isinstance(self._res_object, Application)):
            app = self._res_object

            # Update templates' UUID
            app_files = app.get_files()
            for app_file in app_files:
                app_file.set_template_uuid(uuid_conversion_table.getNewUuid(app_file.get_template_uuid()))
        elif(isinstance(self._res_object, Distribution)):
            dist = self._res_object

            # Update kickstart UUID
            dist.set_kickstart(uuid_conversion_table.getNewUuid(dist.get_kickstart()))
        elif(isinstance(self._res_object, Platform)):
            pass
        elif(isinstance(self._res_object, Organization)):
            pass
        elif(isinstance(self._res_object, Environment)):
            env = self._res_object

            # Update organization
            env.set_organization(uuid_conversion_table.getNewUuid(env.get_organization()))
        elif(isinstance(self._res_object, Host)):
            host = self._res_object
            host.set_distribution(uuid_conversion_table.getNewUuid(host.get_distribution()))
            host.set_environment(uuid_conversion_table.getNewUuid(host.get_environment()))
            host.set_organization(uuid_conversion_table.getNewUuid(host.get_organization()))
            host.set_platform(uuid_conversion_table.getNewUuid(host.get_platform()))
        else:
            raise SyncException("Unsupported resource type")

    def display(self):
        super(ResourceAction, self).display()
        print "Resource:", self._res_object.__class__.__name__

class UpdateResource(ResourceAction):
    def __init__(self, is_fast_forward, res_object):
        super(UpdateResource, self).__init__(is_fast_forward, res_object)

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._res_object.get_uuid()
        self._update_meta_data(uuid_conversion_table)

        if(isinstance(self._res_object, Host)):
            self._res_object.commit(True)
        else:
            self._res_object.commit(False)

        new_uuid = self._res_object.get_uuid()
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(UpdateResource, self).display()
        print "Summary: Update resource " + self._res_object.get_name()

class CreateResource(ResourceAction):
    def __init__(self, is_fast_forward, res_object):
        super(CreateResource, self).__init__(is_fast_forward, res_object)

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._res_object.get_uuid()
        self._update_meta_data(uuid_conversion_table)
        self._res_object.create()
        new_uuid = self._res_object.get_uuid()
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(CreateResource, self).display()
        print "Summary: Create resource " + self._res_object.get_name()

class ActionsQueue:
    def __init__(self):
        self._all_fast_forward = True
        self._actions = []

    def addAction(self, action):
        if(not action.isFastForward()):
            self._all_fast_forward = False
        self._actions.append(action)

    def isFastForward(self):
        return self._all_fast_forward

    def executeActions(self, uuid_conversion_table):
        for a in self._actions:
            a.executeAction(uuid_conversion_table)

    def display(self):
        for a in self._actions:
            print "-"*80
            a.display()
        print "-"*80
