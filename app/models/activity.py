from app.common.database import Db


class Activity(object):
    @staticmethod
    def get_activity_type():
        query = "SELECT id, type FROM t_workout_type"
        result = Db.execute_select_query(query)
        return dict((d['type'], d['id']) for d in result)
