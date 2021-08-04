# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import
from comodit_client.control.abstract import AbstractController
from comodit_client.control.doc import ActionDoc
from comodit_client.control.exceptions import ArgumentException
from . import completions
import sys


class AbstractActionController(AbstractController):

    def __init__(self):
        super(AbstractActionController, self).__init__()
        self._doc = self._get_doc()

        self._register(["run"], self._run, self._print_run_completions)
        self._register(["impact"], self._impact, self._print_impact_completions)

        self._register(["help"], self._help)
        self._default_action = self._help

        self._register_action_doc(self._run_doc())
        self._register_action_doc(self._impact_doc())

    def _help(self, argv):
        self._print_doc()

    def _run(self, argv):
        pass

    def _get_doc(self):
        return "Action on deployed host or hostgroups."

    def _print_run_completions(self, param_num, argv):
        pass

    def _print_impact_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.orchestrations(argv[0]).list())

    def _impact(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        self._get_entity(argv).show()


    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <orchestration_name>", """
        show all actions of orchestration.""")

    def _run_doc(self):
        pass

    def _wait(self, organization, name, context_id):
        if self._config.options.wait:
            try:
                time_out = int(self._config.options.timeout)
            except Exception:
                sys.exit("Invalid format for timeout")

            context = self._get_context(organization, name, context_id)
            context.wait_finished(time_out, self._config.options.debug)

    def _get_context(self, organization, name, context_uuid):
        pass



class WebhookActionController(AbstractActionController):

    def __init__(self):
        super(WebhookActionController, self).__init__()

    def _get_doc(self):
        return "Action for webhook."

    def _run_doc(self):
        return ActionDoc("run", "<org_name> <webhook_name>", """
        run webhook.""")

    def _print_run_completions(self, param_num, argv):
        if param_num < 2:
            self._print_webhook_completions(param_num, argv)

    def _print_webhook_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.webhooks(argv[0]).list())

    def _get_webhook(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        org = argv[0]
        webhook_name = argv[1]
        return self._client.webhook(org, webhook_name)

    def _run(self, argv):
        webhook = self._get_webhook(argv)

        result = webhook.run()
        result.show()

    def _impact(self, argv):
        webhook = self._get_webhook(argv)

        webhook.impact()

class HostActionController(AbstractActionController):
    def __init__(self):
        super(HostActionController, self).__init__()

    def _get_host(self, argv):
        return self._client.hosts(argv[0], argv[1]).get(argv[2])

    def _run(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        org = argv[0]
        orch_name = argv[3]

        result = host.run_orchestration(orch_name)
        self._wait(org, orch_name, result["uuid"])

    def _get_doc(self):
        return "Action on deployed host."

    def _run_doc(self):
        return ActionDoc("run", "<org_name> <env_name> <host_name> <orchestration_name>", """
        run action on given host.""")

    def _print_run_completions(self, param_num, argv):
        if param_num < 4:
            self._print_host_completions(param_num, argv)

    def _print_host_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.environments(argv[0]).list())
        elif len(argv) > 1 and param_num == 2:
            completions.print_entity_identifiers(self._client.hosts(argv[0], argv[1]).list())
        elif len(argv) > 2 and param_num == 3:
            host = self._get_host(argv)
            completions.print_entity_identifiers(host.get_orchestrations().list())

    def _print_impact_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.orchestrations(argv[0]).list())

    def _impact(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        orch_name = argv[1]
        self._client.orchestrations(argv[0]).get(orch_name).show_steps()


class OrchestrationActionController(AbstractActionController):
    def __init__(self):
        super(OrchestrationActionController, self).__init__()
        self._register(["pause"], self._pause, self._print_orchestration_context_completions)
        self._register(["stop"], self._stop, self._print_orchestration_context_completions)
        self._register(["resume"], self._resume, self._print_orchestration_context_completions)
        self._register(["restart"], self._restart, self._print_orchestration_context_completions)

        self._register_action_doc(self._pause_doc())
        self._register_action_doc(self._stop_doc())
        self._register_action_doc(self._resume_doc())
        self._register_action_doc(self._restart_doc())

    def _get_orchestration(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        org = argv[0]
        orch_name = argv[1]
        return self._client.orchestration(org, orch_name)

    def _get_orchestration_context(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments")

        org = argv[0]
        orch_name = argv[1]
        return self._client.orchestrationContext(org, orch_name, argv[2])

    def _pause(self, argv):
        context = self._get_orchestration_context(argv)
        context.pause()

    def _stop(self, argv):
        orchestration = self._get_orchestration_context(argv)
        orchestration.stop()

    def _restart(self, argv):
        orchestration = self._get_orchestration_context(argv)
        orchestration.restart(self._config.options.skip_error)

    def _resume(self, argv):
        orchestration = self._get_orchestration_context(argv)
        orchestration.resume()

    def _run(self, argv):
        orchestration = self._get_orchestration(argv)

        result = orchestration.run()
        self._wait(orchestration.organization, orchestration.name, result["uuid"])

    def _get_doc(self):
        return "Apply actions orchestration on hostgroups"

    def _run_doc(self):
        return ActionDoc("run", "<org_name> <orchestration_name>", """
        run orchestration on host in hostgroups.""")

    def _pause_doc(self):
        return ActionDoc("pause", "<org_name> <orchestration_name> <id>", """
        pause running orchestration on host in hostgroups.""")

    def _stop_doc(self):
        return ActionDoc("stop", "<org_name> <orchestration_name> <id>", """
        stop running orchestration on host in hostgroups.""")

    def _restart_doc(self):
        return ActionDoc("restart", "<org_name> <orchestration_name> <id>", """
        restart when errors occurs on orchestration.
        --skip-error to ignore host in error""")

    def _resume_doc(self):
        return ActionDoc("resume", "<org_name> <orchestration_name> <id>", """
        resume paused orchestration""")

    def _print_run_completions(self, param_num, argv):
        if param_num < 2:
            self._print_orchestration_completions(param_num, argv)

    def _print_orchestration_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.orchestrations(argv[0]).list())

    def _print_orchestration_context_completions(self, param_num, argv):
        if param_num < 2:
            self._print_orchestration_completions(param_num, argv)
        elif param_num == 2:
            completions.print_entity_identifiers(self._client.orchestrationContexts(argv[0], argv[1]).list())

    def _get_entity(self, argv):
        name = argv[1]
        return self._client.orchestrations(argv[0]).get(name)

    def _get_context(self, organization, name, context_uuid):
        return self._client.orchestrationContext(organization, name, context_uuid)



class PipelineActionController(AbstractActionController):
    def __init__(self):
        super(PipelineActionController, self).__init__()
        self._register(["pause"], self._pause, self._print_context_completions)
        self._register(["stop"], self._stop, self._print_context_completions)
        self._register(["resume"], self._resume, self._print_context_completions)

        self._register_action_doc(self._pause_doc())
        self._register_action_doc(self._stop_doc())
        self._register_action_doc(self._resume_doc())

    def _get_context(self, organization, name, context_uuid):
        return self._client.pipelineContext(organization, name, context_uuid)

    def _pause(self, argv):
        context = self._get_context(argv[0],  argv[1], argv[2])
        context.pause()

    def _stop(self, argv):
        context = self._get_context(argv[0],  argv[1], argv[2])
        context.stop()

    def _resume(self, argv):
        context = self._get_context(argv[0],  argv[1], argv[2])
        context.resume()

    def _run(self, argv):
        pipeline = self._get_entity(argv)

        result = pipeline.run()
        print("pipeline started")
        self._wait(pipeline.organization, pipeline.name, result["uuid"])

    def _get_doc(self):
        return "Apply actions pipeline context"

    def _run_doc(self):
        return ActionDoc("run", "<org_name> <pipeline_name>", """
        run pipeline.""")

    def _pause_doc(self):
        return ActionDoc("pause", "<org_name> <pipeline_name> <id>", """
        pause running pipeline.""")

    def _stop_doc(self):
        return ActionDoc("stop", "<org_name> <pipeline_name> <id>", """
        stop running pipeline.""")

    def _resume_doc(self):
        return ActionDoc("resume", "<org_name> <pipeline_name> <id>", """
        resume paused pipeline""")

    def _print_run_completions(self, param_num, argv):
        if param_num < 2:
            self._print_pipeline_completions(param_num, argv)

    def _print_context_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.pipelines(argv[0]).list())

    def _print_pipeline_context_completions(self, param_num, argv):
        if param_num < 2:
            self._print_pipeline_completions(param_num, argv)
        elif param_num == 2:
            completions.print_entity_identifiers(self._client.pipelineContexts(argv[0], argv[1]).list())

    def _get_entity(self, argv):
        name = argv[1]
        return self._client.pipelines(argv[0]).get(name)


class NotificationChannelActionController(AbstractActionController):

    def __init__(self):
        super(NotificationChannelActionController, self).__init__()

    def _get_doc(self):
        return "Action for notification-channels."

    def _run_doc(self):
        return ActionDoc("run", "<org_name> <notification-channel_name>", """
        run notification-channel for test.""")

    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <notification-channel_name>", """
                show notification-channel for test.""")
    def _print_run_completions(self, param_num, argv):
        if param_num < 2:
            self._print_notitication_channel_completions(param_num, argv)

    def _print_notitication_channel_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.notifications(argv[0]).list())

    def _get_notification_channel(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        org = argv[0]
        name = argv[1]
        return self._client.notification(org, name)

    def _run(self, argv):
        notification_channel = self._get_notification_channel(argv)
        notification_channel.run()

    def _impact(self, argv):
        notification_channel = self._get_notification_channel(argv)

        notification_channel.impact()
