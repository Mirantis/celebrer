from oslo_serialization import jsonutils
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def LargeBinary():
    return sa.LargeBinary().with_variant(mysql.LONGBLOB(), 'mysql')


class JsonBlob(sa.TypeDecorator):
    impl = sa.Text

    def process_bind_param(self, value, dialect):
        return jsonutils.dumps(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return jsonutils.loads(value)
        return None
