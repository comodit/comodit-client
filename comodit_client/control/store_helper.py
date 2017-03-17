import json, os

from comodit_client.control.doc import ActionDoc
from comodit_client.api.exceptions import PythonApiException
from comodit_client.config import Config
from comodit_client.control.exceptions import ControllerException
from comodit_client.util.editor import edit_text
from collections import OrderedDict

class StoreHelper(object):
    def __init__(self, ctrl, content_type):
        self._ctrl = ctrl
        self._content_type = content_type
        if content_type == "app":
            self._params = "<org_name> <app_name>"
            self._template = "published_application.json"
            self._type_name = "Application"
            self._label = "application"
        elif content_type == "dist":
            self._params = "<org_name> <dist_name>"
            self._template = "published_distribution.json"
            self._type_name = "Distribution"
            self._label = "distribution"
        else:
            raise PythonApiException("Unhandled type: " + str(content_type))

    def store(self):
        if self._content_type == "app":
            return self._ctrl._client.app_store()
        elif self._content_type == "dist":
            return self._ctrl._client.dist_store()
        else:
            return None

    def get_purchased(self, org):
        if self._content_type == "app":
            return org.purchased_apps()
        elif self._content_type == "dist":
            return org.purchased_dists()
        else:
            return None

    def _publish(self, argv):
        app = self._ctrl._get_entity(argv)

        if not app.published_as is None:
            raise PythonApiException(self._type_name + " has already been published")

        template_json = json.load(open(os.path.join(Config()._get_templates_path(), self._template)))
        template_json[self._label] = app.uuid

        pub_app = self.store()._new(template_json)
        self.store()._create(pub_app)

    def _publish_doc(self):
        return ActionDoc("publish", self._params, """
        Publish """ + self._label + """ to store.""")

    def _unpublish(self, argv):
        app = self._ctrl._get_entity(argv)

        if app.published_as is None:
            raise PythonApiException(self._type_name + " is not published")

        self.store().get(app.published_as, {"org_name" : argv[0]}).delete()

    def _unpublish_doc(self):
        return ActionDoc("unpublish", self._params, """
        Unpublish """ + self._label + """ from store.""")

    def _push(self, argv):
        app = self._ctrl._get_entity(argv)

        if app.published_as is None:
            raise PythonApiException(self._type_name + " is not published")

        pub_app = self.store()._new({"uuid" : app.published_as})
        pub_app.update()

    def _push_doc(self):
        return ActionDoc("push", self._params, """
        Push """ + self._label + """ update to store.""")

    def _pull(self, argv):
        app = self._ctrl._get_entity(argv)

        if app.purchased_as is None:
            raise PythonApiException(self._type_name + " is not purchased")

        org = self._ctrl._client.organizations().get(app.organization)

        pur = self.get_purchased(org)._new({"uuid" : app.purchased_as})
        pur.update()

    def _pull_doc(self):
        return ActionDoc("pull", self._params, """
        Pull """ + self._label + """ update from store.""")

    def _update_authorized(self, argv):
        app = self._ctrl._get_entity(argv)

        if app.published_as is None:
            raise PythonApiException(self._type_name + " is not published")

        try:
            pub = self.store().get(app.published_as, {"org_name" : argv[0]})
        except PythonApiException:
            raise ControllerException("Unable to retrieve entity from store, maybe you forgot to use --org option?")
        updated = edit_text(json.dumps(pub.authorized, indent = 4))
        pub.update_authorized(json.loads(updated, object_pairs_hook=OrderedDict))

    def _update_authorized_doc(self):
        return ActionDoc("update-authorized", "<UUID>", """
        Update authorized organizations of a published entity.""")
