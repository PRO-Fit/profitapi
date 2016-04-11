import os.path

from app import app
from app.models.activity import Activity
from app.scripts.calculate_activity_calories_burnt import calculate_activity_calories_burnt


def last_parsed_activity():
    if os.path.isfile('last_parsed_activty'):
        with open('last_parsed_activty', 'r') as last_activity:
            return int(last_activity.read())
    else:
        return 0


def write_last_parsed_activity(activity_id):
    with open('last_parsed_activty', 'w') as last_activity:
        last_activity.write(str(activity_id))


def get_users_from_activities(activities):
    return list(set([activity.get('user_id') for activity in activities]))


def get_user_goals(start_time, end_time):
    pass


def main():
    with app.app_context():
        # activities = Activity.get_activities_since(last_parsed_activity())
        calculate_activity_calories_burnt(last_parsed_activity())
        # if not activities:
        #     exit()
        # write_last_parsed_activity(activities[len(activities)-1].get('id'))
        # first_activity_time = activities[0].get('start_datetime')
        # last_activity_time = activities[len(activities)-1].get('start_datetime')
        # users = get_users_from_activities(activities)
        # print users
        # for activity in activities:
        #     print "test"
        # print last_parsed_activity()
        # write_last_parsed_activity(str(15))
        # print last_parsed_activity()

if __name__ == '__main__':
    main()
