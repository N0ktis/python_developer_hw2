from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError

DEFAULT_PARAMS = ('postgres','317a251','localhost','5432')

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




def init_connection(user, password, host, port):
    engine = create_engine("postgres://{0}:{1}@{2}:{3}/patients".format(user, password, host, port))
    #base.metadata.create_all(engine)
    return sessionmaker(engine)()



#Flask Web Development
#Flask Mega Tutorial
#flask sqlalchemy
#flasj marshmellow
#ORM, многомодульность, хорошая бизнес-логика/техническая сложность


