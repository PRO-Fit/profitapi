from datetime import datetime, timedelta
import time



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
