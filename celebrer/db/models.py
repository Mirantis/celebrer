import uuid

from oslo_db.sqlalchemy import models
from oslo_utils import timeutils

import sqlalchemy as sa

from sqlalchemy.ext import declarative
from sqlalchemy import orm as sa_orm

from celebrer.db import types


class TimestampMixin(object):
    __protected_attributes__ = set(["created", "updated"])

    id = sa.Column(sa.String(36), primary_key=True,
                   default=lambda: uuid.uuid4().hex)
    created = sa.Column(sa.DateTime, default=timeutils.utcnow,
                        nullable=False)
    updated = sa.Column(sa.DateTime, default=timeutils.utcnow,
                        nullable=False, onupdate=timeutils.utcnow)

    def update(self, values):
        """dict.update() behaviour."""
        self.updated = timeutils.utcnow()
        super(TimestampMixin, self).update(values)

    def __setitem__(self, key, value):
        self.updated = timeutils.utcnow()
        super(TimestampMixin, self).__setitem__(key, value)


class _CelebrerBase(models.ModelBase):
    def to_dict(self):
        dictionary = self.__dict__.copy()
        return dict((k, v) for k, v in dictionary.iteritems()
                    if k != '_sa_instance_state')


Base = declarative.declarative_base(cls=_CelebrerBase)


class Task(Base, TimestampMixin):
    __tablename__ = 'task'

    component_name = sa.Column(sa.String(255), nullable=False)
    service_list = sa.Column(types.JsonBlob(), nullable=False)
    action = sa.Column(sa.String(255), nullable=False)
    statuses = sa_orm.relationship("Status", backref='task',
                                   cascade='save-update, merge, delete')
    report_file = sa.Column(sa.String(255), nullable=True)


class Status(Base, TimestampMixin):
    __tablename__ = 'status'
    task_id = sa.Column(sa.String(36), sa.ForeignKey('task.id'))
    text = sa.Column(sa.Text(), nullable=False)


class Node(Base, TimestampMixin):
    __tablename__ = 'node'

    node_id = sa.Column(sa.String(36), unique=True, nullable=False)
    services = sa_orm.relationship("Service", backref='node',
                                   cascade='save-update, merge, delete')


class Service(Base, TimestampMixin):
    __tablename__ = 'services'

    node_id = sa.Column(sa.String(36), sa.ForeignKey('node.id'))
    name = sa.Column(sa.String(255), nullable=False)
    component = sa.Column(sa.String(255), nullable=False)
    # ToDO(all): Implement service status detection


class Lock(Base):
    __tablename__ = 'locks'
    id = sa.Column(sa.String(50), primary_key=True)
    ts = sa.Column(sa.DateTime, nullable=False)


def register_models(engine):
    """Creates database tables for all models with the given engine."""
    models = (Task, Status, Node, Service, Lock)
    for model in models:
        model.metadata.create_all(engine)


def unregister_models(engine):
    """Drops database tables for all models with the given engine."""
    models = (Task, Status, Node, Service, Lock)
    for model in models:
        model.metadata.drop_all(engine)
