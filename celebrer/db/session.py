"""Session management functions."""
import threading

from oslo_config import cfg
from oslo_db import exception
from oslo_db import options
from oslo_db.sqlalchemy import session as db_session
from oslo_log import log as logging
from oslo_utils import timeutils

from celebrer.db.models import Lock

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

options.set_defaults(CONF)

_FACADE = None
_LOCK = threading.Lock()

MAX_LOCK_RETRIES = 10


def _create_facade_lazily():
    global _LOCK, _FACADE

    if _FACADE is None:
        with _LOCK:
            if _FACADE is None:
                _FACADE = db_session.EngineFacade.from_config(CONF,
                                                              sqlite_fk=True)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_lock(name, session=None):
    if session is None:
        session = get_session()
        nested = False
    else:
        nested = session.transaction is not None
    return _get_or_create_lock(name, session, nested)


def _get_or_create_lock(name, session, nested, retry=0):
    if nested:
        session.begin_nested()
    else:
        session.begin()
    existing = session.query(Lock).get(name)
    if existing is None:
        try:
            # no lock found, creating a new one
            lock = Lock(id=name, ts=timeutils.utcnow())
            lock.save(session)
            return session.transaction
            # lock created and acquired
        except exception.DBDuplicateEntry:
            session.rollback()
            if retry >= MAX_LOCK_RETRIES:
                raise
            else:
                # other transaction has created a lock, repeat to acquire
                # via update
                return _get_or_create_lock(name, session, nested, retry + 1)
    else:
        # lock found, acquiring by doing update
        existing.ts = timeutils.utcnow()
        existing.save(session)
        return session.transaction
