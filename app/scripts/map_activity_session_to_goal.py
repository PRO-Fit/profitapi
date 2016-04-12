import os.path
from datetime import datetime

from app import app
from app.models.activity import Activity
from app.models.goals import Goal
from app.models.sessions import SessionModel
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


def get_datetime_from_activity_timestamp(activity_timestamp):
    return datetime.fromtimestamp(activity_timestamp/1000)


def get_items_by_user_id(item_list):
    items_by_user_id = dict()
    for item in item_list:
        user_item_list = items_by_user_id.get(item.get('user_id'))
        if type(item.get('start_datetime')) is int:
            item['start_datetime'] = get_datetime_from_activity_timestamp(item.get('start_datetime'))
        item_data = {
                'start_datetime': item.get('start_datetime'),
                'end_datetime': item.get('end_datetime'),
                'id': item.get('id')
            }
        if user_item_list:
            user_item_list.append(item_data)
        else:
            items_by_user_id[item.get('user_id')] = [item_data]
    return items_by_user_id


def get_item_id_of_item_inclusive_activity(activity, items_by_user):
    user_id = activity.get('user_id')
    user_items = items_by_user.get(user_id, [])
    item_id = 0
    for item in user_items:
        activity_datetime = get_datetime_from_activity_timestamp(activity.get('start_datetime'))
        if item.get('start_datetime') <= activity_datetime <= item.get('end_datetime'):
            item_id = item.get('id')

    if item_id is None:
        print item
    return item_id


def main():
    with app.app_context():
        activities = Activity.get_activities_since_with_user_bio(last_parsed_activity())
        calculate_activity_calories_burnt(activities)
        if not activities:
            exit()
        write_last_parsed_activity(activities[len(activities)-1].get('id'))
        first_activity_time = get_datetime_from_activity_timestamp(activities[0].get('start_datetime'))
        last_activity_time = get_datetime_from_activity_timestamp(activities[len(activities)-1].get('start_datetime'))
        goals = get_items_by_user_id(Goal.get_user_goals(first_activity_time, last_activity_time))
        sessions = get_items_by_user_id(SessionModel.get_user_sessions(first_activity_time, last_activity_time))
        goal_activities = []
        for activity in activities:
            goal_activities.append(
             "('{0}',{1},{2},{3})".format(activity.get('user_id'),
                                          get_item_id_of_item_inclusive_activity(activity, goals),
                                          activity.get('id'),
                                          get_item_id_of_item_inclusive_activity(activity, sessions))
            )
        Activity.insert_goal_session_activity_mapping(goal_activities)

if __name__ == '__main__':
    main()
