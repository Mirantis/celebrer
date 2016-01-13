import copy
import itertools

import oslo_service.sslutils

import celebrer.common.config
import celebrer.common.wsgi


def build_list(opt_list):
    return list(itertools.chain(*opt_list))


_opt_lists = [
    (None, build_list([
        celebrer.common.config.bind_opts,
        celebrer.common.config.celebrer_opts,
        celebrer.common.wsgi.wsgi_opts
    ])),
]

_opt_lists.extend(oslo_service.sslutils.list_opts())


def list_opts():
    return [(g, copy.deepcopy(o)) for g, o in _opt_lists]