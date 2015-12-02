from celebrer.common import rpc
from celebrer.db import models
from celebrer.db import session


class DiscoveryHandler:

    def discover_services(self, context, services, node_uuid):
        unit = session.get_session()
        with unit.begin():
            node = models.Node()
            node.node_id = node_uuid
            unit.add(node)

            for component, service_list in services.items():
                for service_name in service_list:
                    service = models.Service()
                    service.name = service_name
                    service.component = component
                    service.node_id = node.id
                    unit.add(service)
