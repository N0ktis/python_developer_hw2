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


class DataCheck:
    def _name_check(self, name):
        if not name.isalpha():
            logger_error.error("Name or surname contains invalid characters")
            raise ValueError("Name or surname contains invalid characters")
        return name.capitalize()

    def _birth_check(self, born):
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

    def _phone_check(self, phone):
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

    def _doc_check(self, doc):
        if doc.lower() != "паспорт" and doc.lower() != "загранпаспорт" and doc.lower() != "заграничный паспорт" and \
                doc.lower() != "водительские права" and doc.lower() != "водительское удостоверение":
            logger_error.error("Incorrect document")
            raise ValueError("Incorrect document")
        return doc.lower()

    def _doc_id_check(self, doc_id):
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


class DataAccess(DataCheck):
    def __init__(self, name='атрибут', data_get=None, data_set=None, data_del=None):
        self.data_get = data_get
        self.data_set = data_set
        self.data_del = data_del
        self.name = name

    def __get__(self, obj, objtype):
        return self.data_get(obj, self.name)

    def __set__(self, obj, val):
        if type(val) != str:
            logger_error.error("Incorrect type of input data")
            raise TypeError("Incorrect type of input data")
        if self.name == 'first_name' or self.name == 'last_name':
            self.data_set(obj, self._name_check(val), self.name)
        elif self.name == 'birth_date':
            self.data_set(obj, self._birth_check(val), self.name)
        elif self.name == 'phone':
            self.data_set(obj, self._phone_check(val), self.name)
        elif self.name == 'document_type':
            self.data_set(obj, self._doc_check(val), self.name)
        elif self.name == 'document_id':
            self.data_set(obj, self._doc_id_check(val), self.name)

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
            if ((self._document_type == "паспорт" or self._document_type == "водительские права" or
                 self._document_type == "водительское удостоверение") and len(value) == 12) or \
                    ((self._document_type == "загранпаспорт" or self._document_type == "заграничный паспорт")
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

    first_name = DataAccess('first_name', get_field, set_field, del_field)
    last_name = DataAccess('last_name', get_field, set_field, del_field)
    birth_date = DataAccess('birth_date', get_field, set_field, del_field)
    phone = DataAccess('phone', get_field, set_field, del_field)
    document_type = DataAccess('document_type', get_field, set_field, del_field)
    document_id = DataAccess('document_id', get_field, set_field, del_field)

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
            pnd.read_csv(self.path, sep='|', header=None, dtype=str)
        except pnd.errors.EmptyDataError:
            return
        for i in range(0, len(pnd.read_csv(self.path, sep='|', header=None, dtype=str).index)):
            try:
                pnd.read_csv(self.path, sep='|', header=None, dtype=str)
            except pnd.errors.EmptyDataError:
                return
            yield Patient(*pnd.read_csv(self.path, sep='|', header=None, dtype=str).iloc[i])

    def limit(self, limit_val):
        for i in range(0, limit_val):
            try:
                pnd.read_csv(self.path, sep='|', header=None, nrows=limit_val, dtype=str)
            except pnd.errors.EmptyDataError:
                return
            yield Patient(*pnd.read_csv(self.path, sep='|', header=None, nrows=limit_val, dtype=str).iloc[i])
