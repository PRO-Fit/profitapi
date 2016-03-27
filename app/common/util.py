import time
from datetime import datetime
import phonenumbers


class Util():
    @staticmethod
    def get_current_time():
        return datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_current_datetime():
        return datetime.fromtimestamp(time.time())

    @staticmethod
    def convert_string_to_datetime(datetime_str):
        if len(datetime_str) is 10:
            datetime_str += " 00:00:00"
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def is_valid_contact_number(number):
        return phonenumbers.is_valid_number(phonenumbers.parse(str(number), 'US'))

    @staticmethod
    def clean_contact_number(number):
        number = phonenumbers.parse(str(number), 'US')
        return number.national_number
