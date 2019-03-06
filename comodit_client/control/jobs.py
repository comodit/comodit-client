# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.doc import ActionDoc
from comodit_client.util import prompt


class JobsController(OrganizationEntityController):

    _template = "jobs.json"

    def __init__(self):
        super(JobsController, self).__init__()
        self._register(["run"], self._run, self._print_entity_completions)        
        self._register_action_doc(self._run_doc())
        
        # subcontrollers
        # actions
        self._update_action_doc_params("run", "<org_name> <res_name>")
        
    def _get_collection(self, org_name):
        return self._client.jobs(org_name)

    def _prune_json_update(self, json_wrapper):
        super(JobsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
        
    def _run_doc(self):
        return ActionDoc("run", self._list_params(), """
        run job.""")
        
    def _run(self, argv):
        job = self._get_entity(argv)
        if self._config.options.force or (prompt.confirm(prompt="Run " + job.name + " ?", resp=False)) :
            job.run()