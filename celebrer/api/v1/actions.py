import os
from oslo_log import log as logging
from webob import exc

import json
from celebrer.common import wsgi
from celebrer.common import rpc
from celebrer.db import models
from celebrer.db import session

from oslo_config import cfg

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Controller(object):

    def __init__(self):
        self.conf = CONF

    def list_services(self, request):
        unit = session.get_session()
        return json.dumps([node.to_dict() for node in
                           unit.query(models.Service).all()])

    def run_services(self, request):
        if request.json_body['action'] == 'start':
            return json.dumps(rpc.call(
                'tasks',
                'create_task',
                service_list=request.json_body['services']))
        elif request.json_body['action'] == 'stop':
            return json.dumps(rpc.call(
                'tasks',
                'stop_task',
                task_id=request.json_body['task_id']))

    def get_results(self, request, task_id=None):
        unit = session.get_session()
        if task_id:
            return json.dumps([node.to_dict() for node in
                               unit.query(models.Task).filter_by(id=task_id).
                              first()])
        return json.dumps([node.to_dict() for node in
                           unit.query(models.Task).all()])

    def get_report(self, request, task_id=None):
        unit = session.get_session()
        if not task_id:
            raise exc.HTTPNotFound('Not found task')
        if os.path.isfile('%s/%s' % (self.conf.reports_dir, task_id)):
            return open('%s/%s' % (self.conf.reports_dir, task_id)).read()
        else:
            raise exc.HTTPNotFound('Not found report')

def create_resource():
    return wsgi.Resource(Controller())
