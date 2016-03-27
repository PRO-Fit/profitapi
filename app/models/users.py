from app.common.database import Db
from app.common.util import Util
from app.models.activity import Activity


class User(object):
    @staticmethod
    def insert_user(user_details):
        add_user_query = ("""INSERT INTO t_user (first_name, last_name, points, weight, height, dob, gender, email,
                          contact_number, injuries, user_id, created_datetime, modified_datetime) VALUES (
                          %(first_name)s, %(last_name)s, %(points)s, %(weight)s, %(height)s, %(dob)s, %(gender)s,
                          %(email)s, %(contact_number)s, %(injuries)s, %(user_id)s, %(created_datetime)s,
                          %(modified_datetime)s)""")
        user_details['contact_number'] = Util.clean_contact_number(user_details.get('contact_number'))
        user_details['created_datetime'] = Util.get_current_time()
        user_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(add_user_query, user_details)

    @staticmethod
    def update_user(user_details, user_id):
        update_user_query = """UPDATE t_user
                                SET
                                first_name = '%(first_name)s',
                                last_name = '%(last_name)s',
                                points = %(points)s,
                                weight = %(weight)s,
                                height = %(height)s,
                                dob = '%(dob)s',
                                gender = '%(gender)s',
                                email = '%(email)s',
                                contact_number = %(contact_number)s,
                                injuries = '%(injuries)s',
                                modified_datetime = '%(modified_datetime)s'
                                WHERE user_id = '%(user_id)s'"""
        user_details.update({
            'modified_datetime': Util.get_current_time(),
            'user_id': user_id
        })
        return Db.execute_update_query(update_user_query, user_details)

    @staticmethod
    def insert_user_activity_pref(user_id, preference):
        query = """INSERT INTO t_user_activity_preference (workout_type_id, preference_priority, user_id) VALUES (
                  %s, %s, %s)"""
        activity_types = Activity.get_activity_type()
        for activity in preference:
            activity_query = query % (activity_types.get(activity), int(preference.get(activity)), user_id)
            Db.execute_insert_query(activity_query)
        return

    @staticmethod
    def get_user(user_id):
        get_user_query = """SELECT first_name, last_name, points, weight, height, dob, gender, email, contact_number,
                          injuries FROM t_user WHERE user_id = \"%s\"""" % user_id
        return Db.execute_select_query(get_user_query)

    @staticmethod
    def get_user_activity_pref(user_id):
        query = """SELECT twt.type, preference_priority FROM t_user_activity_preference tuaf
                    INNER JOIN t_workout_type twt ON (tuaf.workout_type_id = twt.id)
                    INNER JOIN t_user tu ON (tuaf.user_id = tu.id) AND tu.user_id = \"%s\"""" % user_id
        result = Db.execute_select_query(query)
        return dict((d['type'], d['preference_priority']) for d in result)

    @staticmethod
    def set_user_activity_pref(user_id, activity_preference):
        query = """UPDATE t_user_activity_preference tuap
                    INNER JOIN t_user tu ON (tuap.user_id = tu.id)
                    SET preference_priority = %(priority)s
                    WHERE tu.user_id = \"%(user_id)s\" AND workout_type_id = %(workout_type)s"""
        activity_types = Activity.get_activity_type()
        success = 1
        for type, priority in activity_preference.iteritems():
            update = {
                'priority': priority,
                'user_id': user_id,
                'workout_type': activity_types.get(type)
            }
            success = Db.execute_update_query(query, update)
            if success is -1:
                break
        return success

    @staticmethod
    def get_user_connections(user_id, contacts=None):
        if contacts:
            get_users_by_contacts_query = """SELECT user_id FROM t_user WHERE contact_number IN ('{}')""".format(",".join(str(number) for number in contacts))
            result = Db.execute_select_query(get_users_by_contacts_query)
            connections = [record['user_id'] for record in result]
            if user_id in connections:
                connections.remove(user_id)
            return connections
        else:
            query = """SELECT connected_user_id FROM t_user_connection WHERE user_id = '%s'""" % user_id
            result = Db.execute_select_query(query)
            connections = [record['connected_user_id'] for record in result]
            if user_id in connections:
                connections.remove(user_id)
            return connections

    @staticmethod
    def set_user_connections(user_id, contacts):
        connections = User.get_user_connections(user_id, contacts)
        insert_connection_query = """INSERT INTO t_user_connection (user_id, connected_user_id) VALUES
                                      (%(user_id)s, %(connected_user_id)s)"""
        for connection in connections:
            map_1_to_2 = {'user_id': str(user_id), 'connected_user_id': str(connection)}
            map_2_to_1 = {'user_id': str(connection), 'connected_user_id': str(user_id)}
            Db.execute_insert_query(insert_connection_query, map_1_to_2)
            Db.execute_insert_query(insert_connection_query, map_2_to_1)
