# coding: utf-8
"""
Provides the importer tool. The importer can be used to importer entities
from local directories into a ComodIT server.
"""
from __future__ import print_function

from builtins import str
from builtins import object
import os

from comodit_client.api.application import Application
from comodit_client.api.collection import EntityNotFoundException
from comodit_client.api.contexts import ApplicationContext, PlatformContext, \
    DistributionContext
from comodit_client.api.distribution import Distribution
from comodit_client.api.environment import Environment
from comodit_client.api.exceptions import PythonApiException
from comodit_client.api.host import Host, Instance
from comodit_client.api.notification import Notification
from comodit_client.api.job import Job
from comodit_client.api.organization import Organization
from comodit_client.api.platform import Platform


class ImportException(Exception):
    """
    Exception raised by importer in case of error.
    """

    pass


class Import(object):
    """
    The importer is a tool that enables to import entities from local
    directories. Imported entities have generally been exported (see L{Export}).
    """

    def __init__(self, skip_conflict = False, queue_actions = False, with_instances=False, update_existing=False):
        """
        Creates an importer instance. When importing entities, there might be
        conflicts with existing remote entities. In this case, import fails unless
        'skip conflicts' flag is set (conflicting entities are not imported).
        This is not a synchronization tool, see L{sync tool<SyncEngine>} for
        this feature.

        The importer can queue actions before executing them on import. This
        allows to audit the actions before actually applying them. It also
        enabled to detect conflicts.

        @param skip_conflict: If true, sets 'skip conflicts' flag.
        @type skip_conflict: bool
        @param queue_actions: If true, enabled queuing mode.
        @type queue_actions: bool
        """

        self._skip_conflict = skip_conflict
        self._queue_actions = queue_actions
        self._with_instances = with_instances
        self._update_existing = update_existing
        if queue_actions:
            self._actions_queue = ActionsQueue()

    def _import_entity_and_detect_conflict(self, local_res, entity_type = "entity", skip_conflict_detection=False):
        conflict = self._detect_conflict(local_res, skip_conflict_detection)
        self._import_entity(local_res, conflict, entity_type)
        return conflict

    def _detect_conflict(self, local_res, skip_conflict_detection=False):
        if not skip_conflict_detection:
            return self._is_conflict(local_res.collection, local_res.name)
        else:
            return False

    def _import_entity(self, local_res, conflict, entity_type = "entity"):
        if conflict:
            if self._update_existing:
                self._update_entity(local_res, entity_type)
            else:
                self._signal_conflict(local_res, entity_type)
        else:
            self._create_entity(local_res, entity_type)

    def _is_conflict(self, collection, res_name):
        try:
            collection.get(res_name)
            return True
        except EntityNotFoundException:
            return False

    def _update_entity(self, local_res, entity_type):
        if self._queue_actions:
            self._actions_queue.add_action(UpdateEntity(local_res, entity_type))
        else:
            local_res.update()

    def _signal_conflict(self, local_res, entity_type):
        if self._queue_actions:
            self._actions_queue.add_action(CreateEntity(True, local_res, entity_type))
        else:
            raise ImportException("There is a conflict for " + entity_type + " '" + local_res.name + "'")

    def _create_entity(self, local_res, entity_type):
        if self._queue_actions:
            self._actions_queue.add_action(CreateEntity(False, local_res, entity_type))
        else:
            local_res.create()

    def _import_instance(self, instance):
        try:
            instance.collection.get()
        except PythonApiException:
            if self._queue_actions:
                self._actions_queue.add_action(CreateEntity(False, instance, "host instance"))
            else:
                instance.create()

    def _import_file_content(self, conflict, src_file, app, name, entity_type = "entity"):
        if self._queue_actions:
            self._actions_queue.add_action(UploadContent(conflict, src_file, app, name, entity_type))
        else:
            app.files().get(name).set_content(src_file)

    def _import_thumbnail(self, conflict, src_file, app, entity_type = "entity"):
        if self._queue_actions:
            self._actions_queue.add_action(UploadThumb(conflict, src_file, app, entity_type))
        else:
            app.set_thumbnail_content(src_file)

    def _import_entity_with_files_and_parameters(self, res, root_folder, entity_type = "entity", skip_conflict_detection=False):
        res.load(root_folder)
        files_to_upload = res.files_f

        conflict = self._detect_conflict(res, skip_conflict_detection)
        if conflict:
            for res_file in res.files_f:
                self._import_entity_and_detect_conflict(res_file, "file", skip_conflict_detection)
            for param in res.parameters_f:
                self._import_entity_and_detect_conflict(param, "parameter", skip_conflict_detection)

        self._import_entity(res, conflict, entity_type)

        # Push files' content
        for f in files_to_upload:
            file_name = f.name
            content_file = os.path.join(root_folder, "files", file_name)
            self._import_file_content(conflict, content_file, res, file_name, entity_type)

        if os.path.exists(os.path.join(root_folder, "thumb")):
            thumb_file = os.path.join(root_folder, "thumb")
            self._import_thumbnail(conflict, thumb_file, res, entity_type)

    def import_application(self, org, root_folder, skip_conflict_detection=False):
        """
        Imports an application from a local folder into a given organization.

        @param org: The target organization.
        @type org: L{Organization}
        @param root_folder: Path to directory containing application's definition.
        @type root_folder: string
        """

        app = Application(org.applications(), None)
        self._import_entity_with_files_and_parameters(app, root_folder, "application", skip_conflict_detection=skip_conflict_detection)

    def import_distribution(self, org, root_folder, skip_conflict_detection=False):
        """
        Imports a distribution from a local folder into a given organization.

        @param org: The target organization.
        @type org: L{Organization}
        @param root_folder: Path to directory containing distribution's definition.
        @type root_folder: string
        """

        dist = Distribution(org.distributions(), None)
        self._import_entity_with_files_and_parameters(dist, root_folder, "distribution", skip_conflict_detection=skip_conflict_detection)

    def import_platform(self, org, root_folder, skip_conflict_detection=False):
        """
        Imports a platform from a local folder into a given organization.

        @param org: The target organization.
        @type org: L{Organization}
        @param root_folder: Path to directory containing platform's definition.
        @type root_folder: string
        """

        plat = Platform(org.platforms(), None)
        self._import_entity_with_files_and_parameters(plat, root_folder, "platform", skip_conflict_detection=skip_conflict_detection)

    def import_environment(self, org, env_folder, skip_conflict_detection=False):
        """
        Imports an environment from a local folder into a given organization.

        @param org: The target organization.
        @type org: L{Organization}
        @param env_folder: Path to directory containing environment's definition.
        @type env_folder: string
        """

        env = Environment(org.environments(), None)
        env.load(env_folder)
        env_already_exists = self._import_entity_and_detect_conflict(env, "environment", skip_conflict_detection=skip_conflict_detection)

        # Push hosts
        hosts_folder = os.path.join(env_folder, "hosts")
        if os.path.exists(hosts_folder):
            hosts_list = os.listdir(hosts_folder)
            for host_name in hosts_list:
                host_folder = os.path.join(hosts_folder, host_name)
                self.import_host(env, host_folder, skip_conflict_detection=not env_already_exists)
                
    def import_jobs(self, org, job_folder, skip_conflict_detection=False):
        """
        Imports a job from a local folder into a given organization.

        @param org: The target organization.
        @type org: L{Organization}
        @param job_folder: Path to directory containing job's definition.
        @type job_folder: string
        """

        job = Job(org.jobs(), None)
        job.load(job_folder)
        job_already_exists = self._import_entity_and_detect_conflict(job, "job", skip_conflict_detection=skip_conflict_detection)

    def import_notifications(self, org, notification_folder, skip_conflict_detection=False):
        """
        Imports a job from a local folder into a given organization.

        @param org: The target organization.
        @type org: L{Organization}
        @param notification_folder: Path to directory containing job's definition.
        @type notification_folder: string
        """

        notification = Notification(org.notifications(), None)
        notification.load(notification_folder)
        notification_already_exists = self._import_entity_and_detect_conflict(notification, "notification", skip_conflict_detection=skip_conflict_detection)

    def import_host(self, env, host_folder, skip_conflict_detection=False):
        """
        Imports a host from a local folder into a given environment.

        @param env: The target environment.
        @type env: L{Environment}
        @param host_folder: Path to directory containing host's definition.
        @type host_folder: string
        """

        host = Host(env.hosts(), None)
        host.load(host_folder)

        apps = host.application_names

        # Contexts are created below
        host._del_field("applications")
        host._del_field("platform")
        host._del_field("distribution")

        host_already_exists = self._import_entity_and_detect_conflict(host, "host", skip_conflict_detection=skip_conflict_detection)

        # Import application contexts
        for app in apps:
            context = ApplicationContext(host.applications(), None)
            context.load_json(os.path.join(host_folder, "applications", app + ".json"))
            self._import_entity_and_detect_conflict(context, "application context", skip_conflict_detection=not host_already_exists)

        # Import platform context
        platform_file = os.path.join(host_folder, "platform.json")
        if os.path.exists(platform_file):
            context = PlatformContext(host.platform(), None)
            context.load_json(platform_file)
            self._import_entity_and_detect_conflict(context, "platform context", skip_conflict_detection=not host_already_exists)

        # Import distribution context
        dist_file = os.path.join(host_folder, "distribution.json")
        if os.path.exists(dist_file):
            context = DistributionContext(host.distribution(), None)
            context.load_json(dist_file)
            self._import_entity_and_detect_conflict(context, "distribution context", skip_conflict_detection=not host_already_exists)

        # Import instance (must come at last)
        instance_file = os.path.join(host_folder, "instance.json")
        if os.path.exists(instance_file) and self._with_instances:
            instance = Instance(host.instance(), None)
            instance.load_json(instance_file)
            self._import_instance(instance)

    def import_organization(self, client, org_folder):
        """
        Imports an organization from a local folder.

        @param client: The client.
        @type client: L{Client}
        @param org_folder: Path to directory containing organization's definition.
        @type org_folder: string
        """

        org = Organization(client.organizations(), None)
        org.load(org_folder)

        organization_already_exists = self._import_entity_and_detect_conflict(org, "organization")

        apps_folder = os.path.join(org_folder, "applications")
        if os.path.exists(apps_folder):
            for app in os.listdir(apps_folder):
                self.import_application(org, os.path.join(apps_folder, app), skip_conflict_detection=not organization_already_exists)

        dists_folder = os.path.join(org_folder, "distributions")
        if os.path.exists(dists_folder):
            for dist in os.listdir(dists_folder):
                self.import_distribution(org, os.path.join(dists_folder, dist), skip_conflict_detection=not organization_already_exists)

        plats_folder = os.path.join(org_folder, "platforms")
        if os.path.exists(plats_folder):
            for plat in os.listdir(plats_folder):
                self.import_platform(org, os.path.join(plats_folder, plat), skip_conflict_detection=not organization_already_exists)

        envs_folder = os.path.join(org_folder, "environments")
        if os.path.exists(envs_folder):
            for env in os.listdir(envs_folder):
                self.import_environment(org, os.path.join(envs_folder, env), skip_conflict_detection=not organization_already_exists)
                
        jobs_folder = os.path.join(org_folder, "jobs")
        if os.path.exists(jobs_folder):
            for job in os.listdir(jobs_folder):
                self.import_jobs(org, os.path.join(jobs_folder,job), skip_conflict_detection=not organization_already_exists)
                
        notifications_folder = os.path.join(org_folder, "notification-channels")
        if os.path.exists(notifications_folder):
            for notification in os.listdir(notifications_folder):
                self.import_notifications(org, os.path.join(notifications_folder,notification), skip_conflict_detection=not organization_already_exists)

    def display_queue(self, show_only_conflicts = True):
        """
        If queuing was enabled, displays the queued actions to standard output.
        This method must be called after a call to one of the C{import_*} methods.
        """

        if not self._queue_actions:
            raise ImportException("Queueing is not enabled")

        self._actions_queue.display_actions(show_only_conflicts)

    def execute_queue(self):
        """
        If queuing was enabled, executes the queued actions to standard output.
        This method must be called after a call to one of the C{import_*} methods.
        """

        if not self._queue_actions:
            raise ImportException("Queueing is not enabled")

        self._actions_queue.apply_actions(self._skip_conflict)

    def no_conflict(self):
        """
        If queuing was enabled, tells if a conflict was detected.
        This method must be called after a call to one of the C{import_*} methods.

        @return: True if a conflict was detected, false otherwise.
        @rtype: bool
        """

        if not self._queue_actions:
            raise ImportException("Queueing is not enabled")

        return self._actions_queue.no_conflict()


class Action(object):
    """
    An import action.
    """

    def __init__(self, conflict):
        """
        Creates a new action instance.

        @param conflict: True if this actions is conflicting.
        @type conflict: bool
        """

        self._conflict = conflict

    def conflict(self):
        """
        Tells if the action is conflicting.

        @return: True if the action is conflicting, false otherwise.
        @rtype: bool
        """

        return self._conflict

    def execute(self):
        """
        Executes this action.
        """

        raise NotImplementedError

    def get_summary(self):
        """
        Provides a description of this action.
        
        @return: A description of this action.
        @rtype: string
        """

        raise NotImplementedError

    def display(self):
        """
        Displays this actions to standard output.
        """

        print("Conflict:", self._conflict)
        print("Summary: " + self.get_summary())


class UploadContent(Action):
    """
    File-upload action.
    """

    def __init__(self, conflict, src_file, res, file_name, entity_type = "entity"):
        """
        Creates a new file-upload action instance.

        @param conflict: True if the action is conflicting, false otherwise.
        @type conflict: bool
        @param src_file: Path to local file to upload.
        @type src_file: string
        @param file_name: Name of the remote file.
        @type file_name: string
        @param entity_type: Entity type.
        @type entity_type: string
        """

        super(UploadContent, self).__init__(conflict)
        self._src_file = src_file
        self._res = res
        self._entity_type = entity_type
        self._file_name = file_name

    def get_summary(self):
        return "Upload file " + self._src_file + " to " + self._entity_type + " '" + self._res.name + "'"

    def execute(self):
        file_res = self._res.get_file(self._file_name)
        file_res.set_content(self._src_file)


class UploadThumb(Action):
    """
    Thumbnail-upload action.
    """

    def __init__(self, conflict, src_file, res, entity_type = "entity"):
        """
        Creates a new thumbnail-upload action instance.

        @param conflict: True if the action is conflicting, false otherwise.
        @type conflict: bool
        @param src_file: Path to local file to upload.
        @type src_file: string
        @param entity_type: Entity type.
        @type entity_type: string
        """

        super(UploadThumb, self).__init__(conflict)
        self._src_file = src_file
        self._res = res
        self._entity_type = entity_type

    def get_summary(self):
        return "Upload thumbnail to " + self._entity_type + " '" + self._res.name + "'"

    def execute(self):
        self._res.set_thumbnail_content(self._src_file)


class CreateEntity(Action):
    """
    Entity creation action.
    """

    def __init__(self, conflict, res_object, entity_type):
        """
        Creates a new create-entity action instance.

        @param conflict: True if the action is conflicting, false otherwise.
        @type conflict: bool
        @param res_object: The entity to create.
        @type res_object: L{Entity}
        @param entity_type: Entity type.
        @type entity_type: string
        """

        super(CreateEntity, self).__init__(conflict)
        self._res_object = res_object
        self._entity_type = entity_type

    def execute(self):
        self._res_object.create()

    def get_summary(self):
        return "Create " + self._entity_type + " '" + self._res_object.name + "'"


class UpdateEntity(Action):
    """
    Entity update action.
    """

    def __init__(self, res_object, entity_type):
        """
        Updates an existing entity.

        @param res_object: The entity to update.
        @type res_object: L{Entity}
        @param entity_type: Entity type.
        @type entity_type: string
        """

        super(UpdateEntity, self).__init__(False)
        self._res_object = res_object
        self._entity_type = entity_type

    def execute(self):
        self._res_object.update()

    def get_summary(self):
        return "Update " + self._entity_type + " '" + self._res_object.name + "'"


class ActionsQueue(object):
    """
    The queue of actions.
    """

    def __init__(self):
        """
        Creates a new queue of actions.
        """

        self._no_conflict = True
        self._actions = []

    def add_action(self, action):
        """
        Adds an action to the queue.
        
        @param action: The action to queue.
        @type action: L{Action}
        """

        if action.conflict():
            self._no_conflict = False
        self._actions.append(action)

    def no_conflict(self):
        """
        Tells if the queue contains a conflicting action.

        @return: True if the queue contains conflicting actions, false otherwise.
        @rtype: bool
        """

        return self._no_conflict

    def apply_actions(self, skip_conflicts):
        """
        Applies queued actions.

        @param skip_conflicts: If true, conflicting actions are not applied.
        @type skip_conflicts: bool
        """

        if not self._no_conflict and not skip_conflicts:
            raise ImportException("Cannot apply actions, conflicts detected")

        for a in self._actions:
            print("-"*80)
            if not a.conflict():
                print("Executing '" + a.get_summary() + "'")
                try:
                    a.execute()
                except Exception as e:
                    print("Error:", str(e))
            else:
                print("Skipping '" + a.get_summary() + "'")
        print("-"*80)

    def display_actions(self, show_only_conflicts):
        """
        Displays queued actions.

        @param show_only_conflicts: If true, only conflicting actions are displayed.
        @type show_only_conflicts: bool
        """

        for a in self._actions:
            if not show_only_conflicts or a.conflict():
                print("-"*80)
                a.display()
        print("-"*80)
