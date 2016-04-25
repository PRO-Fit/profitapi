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

    @staticmethod
    def get_activities_since_with_user_bio(activity_id):
        query = """SELECT tau.id, tau.user_id, tau.workout_type_id, distance, tu.weight, tu.height, tu.dob,
                    tau.start_datetime, tau.end_datetime
                    FROM t_user_activity tau
                    INNER JOIN t_user tu ON (tau.user_id = tu.user_id)
                    WHERE tau.id > %s
                    ORDER BY tau.id ASC""" % activity_id
        return Db.execute_select_query(query)

    @staticmethod
    def update_activity_calories_burnt(activity_id, calories_burnt):
        query = """UPDATE t_user_activity SET
                    calories_burnt = %s
                   WHERE id = %s"""
        return Db.execute_update_query(query % (calories_burnt, activity_id))

    @staticmethod
    def insert_goal_session_activity_mapping(goal_activities):
        query = """ INSERT INTO t_goal_activity (user_id, goal_id, activity_id, session_id)
                    VALUES""" + ",".join(goal_activities)
        return Db.execute_insert_query(query)

    @staticmethod
    def get_activity_by_priority(user_id):
        query = """SELECT twt.type FROM t_user_activity_preference tuap
                    INNER JOIN t_user tu ON tu.id = tuap.user_id
                    INNER JOIN t_workout_type twt ON twt.id = tuap.workout_type_id
                    WHERE tu.user_id = '%s'
                    AND twt.type IN ('walk', 'jog')
                    ORDER BY preference_priority DESC
                """
        return [atype['type'] for atype in Db.execute_select_query(query % user_id)]