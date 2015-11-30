from celebrer.db import models
from celebrer.db import session


def setup_db():
    engine = session.get_engine()
    models.register_models(engine)


def drop_db():
    engine = session.get_engine()
    models.unregister_models(engine)
