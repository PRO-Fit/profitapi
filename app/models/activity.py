from app.common.database import Db


class Activity(object):
    @staticmethod
    def get_activity_type():
        query = "SELECT id, type FROM t_workout_type"
        result = Db.execute_select_query(query)
        return dict((d['type'], d['id']) for d in result)

    @staticmethod
    def get_activities_since(activity_id):
        query = """SELECT id, user_id, start_datetime FROM t_user_activity WHERE id > %s ORDER BY id ASC""" % activity_id
        return Db.execute_select_query(query)
