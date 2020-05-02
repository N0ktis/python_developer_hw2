import datetime
import logging
import pandas as pnd

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


def name_check(name):
    if not name.isalpha():
        logger_error.error("Name or surname contains invalid characters")
        raise ValueError("Name or surname contains invalid characters")
    return name.capitalize()


def birth_check(born):
    if len(born) != 10:
        logger_error.error("Incorrect date length")
        raise ValueError("Incorrect date length")
    born = born[:4] + '-' + born[5:7] + '-' + born[8:]
    for k, i in enumerate(born):
        if i.isdigit() and (0 <= k <= 3 or k == 5 or k == 6 or k == 8 or k == 9):
            continue
        elif (k == 4 or k == 7) and i == '-':
            continue
        else:
            logger_error.error("Date contains invalid characters")
            raise ValueError("Date contains invalid characters")
    if str(datetime.date.today()) >= born:
        return born
    else:
        logger_error.error("Date does not exist yet")
        raise ValueError("Date does not exist yet")


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
            logger_error.error("Phone number contains invalid characters")
            raise ValueError("Phone number contains invalid characters")
    else:
        logger_error.error("Incorrect phone number length")
        raise ValueError("Incorrect phone number length")


def doc_check(doc):
    if doc.lower() != PASSPORT and doc.lower() != INTERNATIONAL_PASS_1 and doc.lower() != INTERNATIONAL_PASS_2 and \
            doc.lower() != DRIVER_LICENSE_1 and doc.lower() != DRIVER_LICENSE_2:
        logger_error.error("Incorrect document")
        raise ValueError("Incorrect document")
    return doc.lower()


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
            logger_error.error("Incorrect document's number length")
            raise ValueError("Incorrect document's number length")
    else:
        logger_error.error("Document number contains invalid characters")
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

    def __set__(self, obj, val):
        if type(val) != str:
            logger_error.error("Incorrect type of input data")
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
            logger_error.error("Fields \"first_name\" and \"last_name\" mustn't be changed")
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
                logger_error.error("Number of characters does not match the type of document")
                raise Exception("Number of characters does not match the type of document")
        if create_flag:
            logger_info.info("Field " + key + " were updated")

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

    def __init__(self, name, surname, born, phone, doc, doc_id):
        self.first_name = name
        self.last_name = surname
        self.birth_date = born
        self.phone = phone
        self.document_type = doc
        self.document_id = doc_id
        logger_info.info("Patient added")

    def __str__(self):
        return (self.first_name + ' ' + self.last_name + ' ' + self.birth_date + ' ' + self.phone + ' ' +
                self.document_type + ' ' + self.document_id)

    def save(self):
        df = pnd.DataFrame({'first name': [self.first_name],
                            'last name': [self.last_name],
                            'birth date': [self.birth_date],
                            'phone': [self.phone],
                            'document type': [self.document_type],
                            'document id': [self.document_id]})
        df.to_csv('data.csv', '|', header=False, index=False, mode='a')
        logger_info.info("Patient saved")

    @staticmethod
    def create(name, surname, born, phone, doc, number):
        return Patient(name, surname, born, phone, doc, number)


class PatientCollection:
    def __init__(self, path_to_file):
        if type(path_to_file) != str:
            logger_error.error("Incorrect type of input path")
            raise TypeError("Incorrect type of input path")
        self.path = path_to_file

    def __iter__(self):
        try:
            for i in range(0, len(pnd.read_csv(self.path, sep='|', header=None, dtype=str).index)):
                yield Patient(*pnd.read_csv(self.path, sep='|', header=None, dtype=str).iloc[i])
        except pnd.errors.EmptyDataError:
            return

    def limit(self, limit_val):

        for i in range(0, limit_val):
            try:
                yield Patient(*pnd.read_csv(self.path, sep='|', header=None, nrows=limit_val, dtype=str).iloc[i])
            except pnd.errors.EmptyDataError:
                return