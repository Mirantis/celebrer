from celebrer.common import rpc
from celebrer.db import models
from celebrer.db import session

from oslo_config import cfg

CONF = cfg.CONF


class DiscoveryHandler:

    def __init__(self):
        self.conf = CONF

    def discover_services(self, context, services, node_uuid):
        unit = session.get_session()

        node = unit.query(models.Node).filter_by(node_id=node_uuid).first()
        if not node:
            with unit.begin():
                node = models.Node()
                node.node_id = node_uuid
                unit.add(node)

        with unit.begin():
            for component, service_list in services.items():
                for service_name in service_list:
                    service = unit.query(models.Service).filter_by(node_id=node.id, name=service_name).first()
                    if not service:
                        service = models.Service()
                        service.name = service_name
                        service.component = component
                        service.node_id = node.id
                        service.status = 'Ready'
                        unit.add(service)
                    else:
                        service.status = 'Ready'


class ReportsHandler:

    def __init__(self):
        self.conf = CONF

    def set_status(self, context, status):
        unit = session.get_session()
        with unit.begin():
            status_object = models.Status()
            status_object.task_id = status['task_id']
            status_object.text = status['status']

            service = unit.query(models.Service).filter_by(
                node_id=status['server_id'],
                name=status['service_name']
            ).first()

            service.status = status['status']
            unit.add(status_object)

    def collect_report(self, context, component_name, binary_data, task_id):
        unit = session.get_session()
        with unit.begin():
            task = unit.query(models.Task).filter_by(id=task_id).first()
            report_path = '%s/%s_%s' % (
                    self.conf.reports_dir,
                    component_name,
                    task_id)
            with open(report_path, 'w') as f:
                f.write(binary_data.decode('base64'))
            task.status = 'Finished'
            task.report_file = report_path


class TasksHandler:

    def __init__(self):
        self.conf = CONF

    def create_task(self, context, component_name, service_list):
        unit = session.get_session()
        task_object = models.Task()
        task_object.status = 'Scheduled'
        task_object.component_name = component_name
        task_object.service_list = service_list
        task_object.action = 'start'

        with unit.begin():
            unit.add(task_object)

        rpc.cast(component_name, 'handle_task', task={
            'action': 'start',
            'services': service_list,
            'id': task_object.id
        })
        return {'task_id': task_object.id}

    def stop_task(self, context, task_id):
        unit = session.get_session()
        task_object = unit.query(models.Task).filter_by(id=task_id).first()
        task_object.status = 'Stopping'
        task_object.action = 'stop'
        with unit.begin():
            unit.add(task_object)

        rpc.cast(task_object.component_name, 'handle_task', task={
            'action': 'stop',
            'services': task_object.service_list,
            'task_id': task_object.id
        })

    def get_report(self, context, task_id):
        unit = session.get_session()
        task_object = unit.query(models.Task).filter_by(id=task_id).first()
        task_object.status = 'Generating'
        task_object.action = 'gen_report'
        with unit.begin():
            unit.add(task_object)

        rpc.call('collector', 'handle_task', task={
            'action': 'stop',
            'component_name': task_object.component_name,
            'task_id': task_object.id
        })
