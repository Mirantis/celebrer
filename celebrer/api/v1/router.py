import routes

from celebrer.api.v1 import actions
from celebrer.common import wsgi


class APIv1(wsgi.Router):
    @classmethod
    def factory(cls, global_conf, **local_conf):
        return cls(routes.Mapper())

    def __init__(self, mapper):
        actions_resource = actions.create_resource()
        mapper.connect('/services',
                       controller=actions_resource,
                       action='list_services',
                       conditions={'method': ['GET']}, path='')

        mapper.connect('/services',
                       controller=actions_resource,
                       action='run_services',
                       conditions={'method': ['POST']}, path='')

        mapper.connect('/reports',
                       controller=actions_resource,
                       action='get_results',
                       conditions={'method': ['GET']}, path='')

        mapper.connect('/reports/{task_id}',
                       controller=actions_resource,
                       action='get_results',
                       conditions={'method': ['GET']}, path='')

        mapper.connect('/reports/{task_id}/download',
                       controller=actions_resource,
                       action='get_report',
                       conditions={'method': ['GET']}, path='')

        super(APIv1, self).__init__(mapper)