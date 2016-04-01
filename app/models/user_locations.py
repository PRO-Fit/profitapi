from app.common.database import Db
from app.common.util import Util


class UserLocation(object):
    @staticmethod
    def insert_user_location(user_id, location):
        query = """INSERT INTO t_user_location (user_id, latitude, longitude, timestamp) VALUES (%(user_id)s,
                    %(latitude)s, %(longitude)s, %(timestamp)s)"""
        params = {
            'user_id': user_id,
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'timestamp': Util.get_current_time()
        }
        Db.execute_insert_query(query, params)

