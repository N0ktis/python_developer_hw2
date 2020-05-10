import datetime
import logging
from functools import wraps
from db_config import init_connection, Patient_DB, SQLAlchemyError, NoSuchTableError, DEFAULT_PARAMS

logger_info = logging.getLogger("patient_log_info")
logger_info.setLevel(logging.INFO)
logger_error = logging.getLogger("patient_log_error")
logger_error.setLevel(logging.ERROR)

formatter = logging.Formatter("%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s")

error_logs = logging.FileHandler('error_log.txt', 'a', 'utf-8')
error_logs.setFormatter(formatter)

info_logs = logging.FileHandler('info_log.txt', 'a', 'utf-8')
info_logs.setFormatter(formatter)

logger_info.addHandler(info_logs)
logger_error.addHandler(error_logs)

PASSPORT = 'паспорт'
INTERNATIONAL_PASS_1 = 'загранпаспорт'
INTERNATIONAL_PASS_2 = 'заграничный паспорт'
DRIVER_LICENSE_1 = 'водительское удостоверение'
DRIVER_LICENSE_2 = 'водительские права'


def logger_decorator_maker(id=None):
    def logger_decorator(fun):
        @wraps(fun)
        def wrapper(value, *args):

            global checked_value
            try:
                checked_value = fun(value, *args)
            except ValueError as error:
                logger_error.error(error.args[0])
                raise ValueError(error.args[0])
            except TypeError as error:
                logger_error.error(error.args[0])
                raise TypeError(error.args[0])
            except AttributeError as error:
                logger_error.error(error.args[0])
                raise AttributeError(error.args[0])
            except NoSuchTableError:
                logger_error.error('The table does not exist or is not visible for the join.')
                raise Exception('The table does not exist or is not visible for the join.')
            except SQLAlchemyError:
                logger_error.error('Error while working with database')
                raise Exception('Error while working with database')
            else:
                if id == 'init':
                    logger_info.info("Patient added")
                elif id == 'patient_set' and checked_value:
                    logger_info.info("Field " + args[1] + " were updated")
                elif id == 'save':
                    logger_info.info("Patient saved")
                elif id == 'init connection':
                    logger_info.info("Connect to DB successful")

            return checked_value

        return wrapper

    return logger_decorator


@logger_decorator_maker()
def name_check(name):
    if not name.isalpha():
        raise ValueError("Name or surname contains invalid characters")
    return name.capitalize()


@logger_decorator_maker()
def birth_check(born):
    if len(born) != 10:
        raise ValueError("Incorrect date length")
    born = born[:4] + '-' + born[5:7] + '-' + born[8:]
    for k, i in enumerate(born):
        if i.isdigit() and (0 <= k <= 3 or k == 5 or k == 6 or k == 8 or k == 9):
            continue
        elif (k == 4 or k == 7) and i == '-':
            continue
        else:
            raise ValueError("Date contains invalid characters")
    if str(datetime.date.today()) >= born:
        return born
    else:
        raise ValueError("Date does not exist yet")


@logger_decorator_maker()
def phone_check(phone):
    phone = phone.replace('+', '')
    phone = phone.replace('(', '')
    phone = phone.replace(')', '')
    phone = phone.replace('-', '')
    phone = phone.replace(' ', '')
    if len(phone) == 11:
        if phone.isdigit():
            return "+7" + phone[1:]
        else:
            raise ValueError("Phone number contains invalid characters")
    else:
        raise ValueError("Incorrect phone number length")


@logger_decorator_maker()
def doc_check(doc):
    if doc.lower() != PASSPORT and doc.lower() != INTERNATIONAL_PASS_1 and doc.lower() != INTERNATIONAL_PASS_2 and \
            doc.lower() != DRIVER_LICENSE_1 and doc.lower() != DRIVER_LICENSE_2:
        raise ValueError("Incorrect document")
    return doc.lower()


@logger_decorator_maker()
def doc_id_check(doc_id):
    doc_id = doc_id.replace(' ', '')
    doc_id = doc_id.replace('-', '')
    doc_id = doc_id.replace('/', '')
    doc_id = doc_id.replace('\\', '')
    if doc_id.isdigit():
        if len(doc_id) == 10:
            return doc_id[:2] + ' ' + doc_id[2:4] + ' ' + doc_id[4:]
        elif len(doc_id) == 9:
            return doc_id[:2] + ' ' + doc_id[2:]
        else:
            raise ValueError("Incorrect document's number length")
    else:
        raise ValueError("Document number contains invalid characters")


# Descriptor
class DataAccess:
    def __init__(self, name='атрибут', data_get=None, data_set=None, data_del=None, data_check=None):
        self.data_get = data_get
        self.data_set = data_set
        self.data_del = data_del
        self.data_check = data_check
        self.name = name

    def __get__(self, obj, objtype):
        return self.data_get(obj, self.name)

    @logger_decorator_maker()
    def __set__(self, obj, val):
        if type(val) != str:
            raise TypeError("Incorrect type of input data")
        self.data_set(obj, self.data_check(val), self.name)

    def __delete__(self, obj):
        self.data_del(obj, self.name)


class Patient:
    def get_field(self, key):
        if key == 'first_name':
            return self._first_name
        elif key == 'last_name':
            return self._last_name
        elif key == 'birth_date':
            return self._birth_date
        elif key == 'phone':
            return self._phone
        elif key == 'document_type':
            return self._document_type
        elif key == 'document_id':
            return self._document_id

    @logger_decorator_maker('patient_set')
    def set_field(self, value, key):
        create_flag = True
        if not hasattr(self, '_' + key):
            create_flag = False
        if key == 'first_name' and not hasattr(self, '_first_name'):
            self._first_name = value
        elif key == 'last_name' and not hasattr(self, '_last_name'):
            self._last_name = value
        elif (key == 'first_name' and hasattr(self, '_first_name')) or (
                key == 'last_name' and hasattr(self, '_last_name')):
            raise AttributeError("Fields \"first_name\" and \"last_name\" mustn't be changed")
        elif key == 'birth_date':
            self._birth_date = value
        elif key == 'phone':
            self._phone = value
        elif key == 'document_type':
            self._document_type = value
        elif key == 'document_id':
            if ((self._document_type == PASSPORT or self._document_type == DRIVER_LICENSE_1 or
                 self._document_type == DRIVER_LICENSE_2) and len(value) == 12) or \
                    ((self._document_type == INTERNATIONAL_PASS_1 or self._document_type == INTERNATIONAL_PASS_2)
                     and len(value) == 10):
                self._document_id = value
            else:
                raise ValueError("Number of characters does not match the type of document")
        return create_flag

    def del_field(self, key):
        if key == 'first_name':
            del self._first_name
        elif key == 'last_name':
            del self._last_name
        elif key == 'birth_date':
            del self._birth_date
        elif key == 'phone':
            del self._phone
        elif key == 'document_type':
            del self._document_type
        elif key == 'document_id':
            del self._document_id

    first_name = DataAccess('first_name', get_field, set_field, del_field, name_check)
    last_name = DataAccess('last_name', get_field, set_field, del_field, name_check)
    birth_date = DataAccess('birth_date', get_field, set_field, del_field, birth_check)
    phone = DataAccess('phone', get_field, set_field, del_field, phone_check)
    document_type = DataAccess('document_type', get_field, set_field, del_field, doc_check)
    document_id = DataAccess('document_id', get_field, set_field, del_field, doc_id_check)

    @logger_decorator_maker('init')
    def __init__(self, name, surname, born, phone, doc, doc_id):
        self.first_name = name
        self.last_name = surname
        self.birth_date = born
        self.phone = phone
        self.document_type = doc
        self.document_id = doc_id

    def __str__(self):
        return (self.first_name + ' ' + self.last_name + ' ' + self.birth_date + ' ' + self.phone + ' ' +
                self.document_type + ' ' + self.document_id)

    @logger_decorator_maker('save')
    def save(self):
        session = init_connection(*DEFAULT_PARAMS)
        patient = Patient_DB(first_name=self.first_name, last_name=self.last_name, birth_date=self.birth_date,
                             phone=self.phone, document_type=self.document_type, document_id=self.document_id)
        session.add(patient)
        session.commit()

    @staticmethod
    def create(name, surname, born, phone, doc, number):
        return Patient(name, surname, born, phone, doc, number)


class PatientCollection:
    @logger_decorator_maker('init connection')
    def __init__(self, user, password, host, port):
        if isinstance(user, str) and isinstance(password, str) and isinstance(host, str) and isinstance(port, str):
            self.session = init_connection(user, password, host, port)
        else:
            raise TypeError("Incorrect type of input data")

    @logger_decorator_maker()
    def __iter__(self):
        for patient in self.session.query(Patient_DB):
            yield Patient(patient.first_name, patient.last_name, patient.birth_date, patient.phone,
                          patient.document_type, patient.document_id)

    @logger_decorator_maker()
    def limit(self, limit_val):
        for patient in self.session.query(Patient_DB).limit(limit_val):
            yield Patient(patient.first_name, patient.last_name, patient.birth_date, patient.phone,
                          patient.document_type, patient.document_id)
