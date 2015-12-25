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

            node = unit.query(models.Node).filter_by(node_id=status['server_id']).first()

            service = unit.query(models.Service).filter_by(
                node_id=node.id,
                name=status['service_name']
            ).first()

            service.status = status['status']
            unit.add(status_object)

    def collect_report(self, context, component_name, binary_data, task_id):
        unit = session.get_session()
        with unit.begin():
            task = unit.query(models.Task).filter_by(id=task_id).first()
            report_path = '%s/%s' % (
                    self.conf.reports_dir,
                    task_id)
            with open(report_path, 'w') as f:
                f.write(binary_data.decode('base64'))
            task.status = 'Finished'
            task.report_file = report_path


class TasksHandler:

    def __init__(self):
        self.conf = CONF

    def create_task(self, context, service_list):
        unit = session.get_session()
        task_object = models.Task()
        task_object.status = 'Scheduled'
        component_name = []
        for component in service_list:
            cur_component = component.split('-', 1)
            if cur_component not in component_name:
                component_name.append(cur_component)
        task_object.service_list = service_list
        task_object.action = 'start'

        with unit.begin():
            unit.add(task_object)
        tasks_list = []
        for component in component_name:
            current_service_list = []
            if component in service_list:
                current_service_list.append(component)
                rpc.cast(component_name, 'handle_task', task={
                    'action': 'start',
                    'services': current_service_list,
                    'id': task_object.id
                })
                tasks_list.append(task_object.id)

        return {'task_id': tasks_list}

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
            'id': task_object.id
        })

    def get_report(self, context, task_id):
        unit = session.get_session()
        task_object = unit.query(models.Task).filter_by(id=task_id).first()
        task_object.status = 'Generating'
        task_object.action = 'gen_report'
        with unit.begin():
            unit.add(task_object)

        rpc.call('collector', 'handle_task', task={
            'action': 'gen_report',
            'component_name': task_object.component_name,
            'id': task_object.id
        })
