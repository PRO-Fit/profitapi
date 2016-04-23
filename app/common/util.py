from datetime import datetime, timedelta, date
import time
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
    def convert_datetime_to_str(list_of_rows):
        for row in list_of_rows:
            for key, value in row.iteritems():
                if type(value) is datetime:
                    row[key] = str(value)
        return list_of_rows

    @staticmethod
    def convert_time_to_str(list_of_rows):
        for row in list_of_rows:
            for key, value in row.iteritems():
                if type(value) is timedelta:
                    row[key] = str(value)
        return list_of_rows

    @staticmethod
    def convert_string_to_time(time_str):
        return time.strptime(time_str, '%H:%M:%S')

    @staticmethod
    def is_valid_contact_number(number):
        return phonenumbers.is_valid_number(phonenumbers.parse(str(number), 'US'))

    @staticmethod
    def clean_contact_number(number):
        number = phonenumbers.parse(str(number), 'US')
        return number.national_number

    @staticmethod
    def get_future_date(days_in_future=7):
        return datetime.combine(date.today() + timedelta(days=days_in_future), datetime.min.time())

    @staticmethod
    def get_weekday(date):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dayNumber = date.weekday()
        return days[dayNumber]

    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)
