from oslo_log import log as logging
from webob import exc

from celebrer.common import wsgi
from celebrer.db import session as db_session


LOG = logging.getLogger(__name__)


class Controller(object):

    def get_results(self, request, task_id):
        LOG.debug('Action:GetResult <TaskId: {0}>'.format(task_id))

        unit = db_session.get_session()
        # result = actions.ActionServices.get_result(task_id, unit)
        result = None

        if result is not None:
            return result

        msg = 'Result for task with task_id: {} was not found.'.format(task_id)

        LOG.error(msg)
        raise exc.HTTPNotFound(msg)

    def create_action(self, request):
        LOG.debug('Action:Create')

        try:
            unit = db_session.get_session()
            # task_id = actions.ActionServices.submit_task(
            #    request.json_body['action'], request.json_body['object_id'],
            #    request.json_body['args'], 'test_token', unit)

            return {'action_id': None}
        except KeyError:
            return {
                'error': 'Unable to create action'
            }


def create_resource():
    return wsgi.Resource(Controller())
