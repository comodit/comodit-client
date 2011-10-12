__all__= ["ActionsQueue",
          "UuidConversionTable",
          "CreateResource",
          "UpdateResource",
          "UpdateTemplateAction",
          "CreateTemplateAction"]

import os, json, urlparse

from cortex_client.util import fileupload

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
        raise NotImplemented

    def display(self):
        print "Fast-forward:", self._is_fast_forward

class TemplateAction(Action):
    def __init__(self, is_fast_forward, client, template_folder, template_meta):
        super(TemplateAction, self).__init__(is_fast_forward)
        self._client = client
        self._template_folder = template_folder
        self._template_meta = template_meta

class UpdateTemplateAction(TemplateAction):
    def __init__(self, is_fast_forward, client, template_folder, template_meta):
        super(UpdateTemplateAction, self).__init__(is_fast_forward, client,
                                                   template_folder, template_meta)

    def _update_template(self, uuid, file_name):
        with open(file_name, 'r') as f:
            url = urlparse.urlparse(self._client.endpoint + "/files/" + uuid)
            response = fileupload.post_multipart(url.netloc, url.path,
                                             [("test", "none")],
                                             [("file", file_name, f.read())],
                                             {"Authorization": "Basic " +
                                              (self._client.username + ":" +
                                               self._client.password).encode("base64").rstrip()})
        result = json.loads(response);
        return result[0]

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._template_meta["uuid"]
        new_uuid = self._update_template(old_uuid, os.path.join(self._template_folder,
                                                          self._template_meta["name"]))
        self._client.update("files/" + new_uuid + "/_meta", self._template_meta)
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(UpdateTemplateAction, self).display()
        print "Update template "+self._template_meta["name"]

class CreateTemplateAction(TemplateAction):
    def __init__(self, is_fast_forward, client, template_folder, template_meta_data):
        super(CreateTemplateAction, self).__init__(is_fast_forward, client,
                                                   template_folder,
                                                   template_meta_data)

    def _upload_template(self, file_name):
        with open(file_name, 'r') as f:
            url = urlparse.urlparse(self._client.endpoint + "/files")
            response = fileupload.post_multipart(url.netloc, url.path,
                                                 [("test", "none")],
                                                 [("file", file_name, f.read())],
                                                 {"Authorization": "Basic " +
                                                  (self._client.username + ":" +
                                                   self._client.password).encode("base64").rstrip()})

        result = json.loads(response);
        return result[0]

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._template_meta["uuid"]
        new_uuid = self._upload_template(os.path.join(self._template_folder,
                                                      self._template_meta["name"]))

        self._template_meta["uuid"] = new_uuid
        self._client.update("files/" + new_uuid + "/_meta", self._template_meta)
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(CreateTemplateAction).display()
        print "Create template "+self._template_meta["name"]

class ResourceAction(Action):
    def __init__(self, is_fast_forward, resource_type, meta_data):
        super(ResourceAction, self).__init__(is_fast_forward)
        self._resource_type = resource_type
        self._meta_data = meta_data

    def _update_meta_data(self, uuid_conversion_table):
        if(self._resource_type == "applications"):
            # Update templates' UUID
            app_files = self._meta_data["files"]
            for app_file in app_files:
                app_file["template"] = uuid_conversion_table.getNewUuid(app_file["template"])
        elif(self._resource_type == "distributions"):
            # Update kickstart UUID
            self._meta_data["kickstart"] = uuid_conversion_table.getNewUuid(self._meta_data["kickstart"])
        elif(self._resource_type == "platforms"):
            pass
        elif(self._resource_type == "organizations"):
            # Clear environments (they will be re-added later)
            if(self._meta_data.has_key("environments")):
                del self._meta_data["environments"]
        elif(self._resource_type == "environments"):
            # Clear hosts (they will be re-added later)
            if(self._meta_data.has_key("hosts")):
                del self._meta_data["hosts"]
            # Update organization
            self._meta_data["organization"] = uuid_conversion_table.getNewUuid(self._meta_data["organization"])
        elif(self._resource_type == "hosts"):
            self._meta_data["distribution"] = uuid_conversion_table.getNewUuid(self._meta_data["distribution"])
            self._meta_data["environment"] = uuid_conversion_table.getNewUuid(self._meta_data["environment"])
            self._meta_data["organization"] = uuid_conversion_table.getNewUuid(self._meta_data["organization"])
            self._meta_data["platform"] = uuid_conversion_table.getNewUuid(self._meta_data["platform"])
        else:
            print "Unsupported resource type", self._resource_type

    def display(self):
        super(ResourceAction, self).display()
        print "ResType:", self._resource_type

class UpdateResource(ResourceAction):
    def __init__(self, is_fast_forward, client, resource_type, meta_data):
        super(UpdateResource, self).__init__(is_fast_forward, resource_type,
                                             meta_data)
        self._client = client

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._meta_data["uuid"]
        self._update_meta_data(uuid_conversion_table)
        parameters = {}
        if(self._resource_type == "hosts"):
            parameters["force"] = "true"
        new_uuid = self._client.update(self._resource_type + "/" + self._meta_data["uuid"],
                            self._meta_data, parameters)["uuid"]
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(UpdateResource, self).display()
        print "Update resource "+self._meta_data["name"]

class CreateResource(ResourceAction):
    def __init__(self, is_fast_forward, client, resource_type, meta_data):
        super(CreateResource, self).__init__(is_fast_forward, resource_type, meta_data)
        self._client = client

    def executeAction(self, uuid_conversion_table):
        old_uuid = self._meta_data["uuid"]
        self._update_meta_data(uuid_conversion_table)
        new_uuid = self._client.create(self._resource_type, self._meta_data)["uuid"]
        uuid_conversion_table.putUuidPair(old_uuid, new_uuid)

    def display(self):
        super(CreateResource).display(self)
        print "Create resource "+self._meta_data["name"]

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
            print "------------------------------------------------------------"
            a.display()