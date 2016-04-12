from dateutil.relativedelta import relativedelta

from app.models.activity import Activity
from app.common.util import Util


ACTIVITY_MET = {
    'walk': 3.6,
    'jog': 7,
    'stand': 1.5,
    'sit': 1,
    'up': 4,
    'down': 3,
}


def calculate_age(dob):
    return relativedelta(Util.get_current_datetime(), dob).years


def calculate_bmr(weight, height, age, gender, duration_in_seconds):
    if gender is 'Male':
        return (((13.397 * weight) + (4.799 * height) - (5.677 * age) + 88.362) * duration_in_seconds) / (24 * 60 * 60)
    else:
        return (((9.247 * weight) + (3.098 * height) - (4.330 * age) + 447.593) * duration_in_seconds) / (24 * 60 * 60)


def calculate_calories_burnt_for_activity(bmr, activity_type_id):
    activity_types = Activity.get_activity_type()
    activity_type_by_id = {v: k for k, v in activity_types.items()}
    return bmr * ACTIVITY_MET.get(activity_type_by_id.get(activity_type_id, None), 1)


def calculate_activity_calories_burnt(activities):
    for activity in activities:
        age = calculate_age(activity.get('dob'))
        bmr = calculate_bmr(activity.get('weight'), activity.get('weight'), age, activity.get('gender'), 5)
        calories = calculate_calories_burnt_for_activity(bmr, activity.get('workout_type_id'))
        Activity.update_activity_calories_burnt(activity.get('id'), calories)
