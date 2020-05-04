from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEFAULT_URL = "postgres://postgres:317a251@localhost:5432/patients"

base = declarative_base()


class Patient_DB(base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(String)
    phone = Column(String)
    document_type = Column(String)
    document_id = Column(String)


def init_connection(user='', password='', host='', port='', dbname=''):
    engine = create_engine("postgres://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, dbname))
    return sessionmaker(engine)()
