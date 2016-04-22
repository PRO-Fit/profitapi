import operator
from datetime import date

from app.common.database import Db
from app.common.util import Util
from app.models.goals import Goal

TIME_SLOTS = Db.execute_select_query("SELECT * FROM t_time_slots_to_recommend ")
TIME_SLOTS_BY_ID = {slot['id']: slot for slot in TIME_SLOTS}


def get_user_session_count_by_start_end_time():
    #TODO: Add date range condition
    query = """SELECT
                user_id,
                count(*) session_count,
                TIME(start_datetime) start_time,
                TIME(end_datetime) end_time
            FROM t_user_session
            GROUP BY user_id, start_time, end_time"""
    return Db.execute_select_query(query)


def get_calories_burnt_for_top_slots(user_id, slot_ids):
    #TODO: Add date range condition
    query = """SELECT ttstr.id, TRUNCATE(SUM(calories_burnt), 2) as calories
            FROM t_user_activity tua, t_time_slots_to_recommend ttstr
            WHERE TIME(TRUNCATE(FROM_UNIXTIME(start_datetime/1000),0)) BETWEEN ttstr.start_time AND ttstr.end_time
              AND ttstr.id IN (%s)
              AND tua.user_id = '%s'
            GROUP BY tua.user_id, ttstr.id
    """
    return {slot.get('id'): slot.get('calories') for slot in Db.execute_select_query(query % (",".join(map(str, slot_ids)), user_id))}


def get_required_calories_per_day_for_goals(goal_ids):
    query = """SELECT
                goal_id,
                CASE
                    WHEN tg.start_datetime <= CURRENT_DATE THEN ABS(TRUNCATE((target_burn_calories - SUM(calories_burnt))/DATEDIFF(tg.end_datetime, CURRENT_DATE),2))
                    ELSE ABS(TRUNCATE((target_burn_calories - SUM(calories_burnt))/DATEDIFF(tg.end_datetime, tg.start_datetime),2))
                END as cal_per_day
                FROM t_goal tg, t_goal_activity tga, t_user_activity ta
                WHERE tg.id = tga.goal_id AND tga.activity_id = ta.id
                AND tg.id IN (%s)
                GROUP BY goal_id"""
    print query % ",".join(map(str, goal_ids))
    return {goal.get('goal_id'): goal.get('cal_per_day') for goal in Db.execute_select_query(query % ",".join(map(str, goal_ids)))}


def get_time_slot_for_session(user_session):
    slot_id = None
    for slot in TIME_SLOTS:
        if slot['start_time'] <= user_session['start_time'] <= user_session['end_time'] <= slot['end_time']:
            slot_id = slot['id']

    if not slot_id:
        slot1 = None
        slot2 = None
        for slot in TIME_SLOTS:
            if slot['start_time'] <= user_session['start_time'] <= slot['end_time']:
                slot1 = slot
            if slot['start_time'] <= user_session['end_time'] <= slot['end_time']:
                slot2 = slot

        slot1_overlap = slot1['end_time'] - user_session['start_time']
        slot2_overlap = user_session['end_time'] - slot2['start_time']
        slot_id = slot1['id'] if slot1_overlap > slot2_overlap else slot2['id']
    return slot_id


def get_number_of_sessions_each_time_slots():
    user_session_count = get_user_session_count_by_start_end_time()
    user_sessions_by_user = dict()
    for user_session in user_session_count:
        slot_id = get_time_slot_for_session(user_session)
        if user_session['user_id'] in user_sessions_by_user:
            user = user_sessions_by_user.get(user_session['user_id'])
            user[slot_id] = user.get(slot_id, 0) + user_session.get('session_count')
        else:
            user_sessions_by_user[user_session['user_id']] = {
                slot_id: user_session.get('session_count')
            }
    for user in user_sessions_by_user:
        user_sessions_by_user[user] = dict(sorted(user_sessions_by_user[user].items(), key=operator.itemgetter(1), reverse=True)[:5])
    # NOW user_sessions_by_user HAS TOP 5 slots based on number of sessions per slot
    # FORMAT = {'user_id': {slot_id: number_of_sessions}}
    return user_sessions_by_user


def get_top_time_slots_for_users():
    top_slots_by_user = get_number_of_sessions_each_time_slots()
    for user in top_slots_by_user:
        calories_for_slots = get_calories_burnt_for_top_slots(user, list(top_slots_by_user[user].keys()))
        user_slots = top_slots_by_user[user]
        for slot in user_slots:
            user_slots[slot] = {
                'session_count': user_slots[slot],
                'calories': calories_for_slots.get(slot, 0),
                'start_time': TIME_SLOTS_BY_ID[slot].get('start_time'),
                'end_time': TIME_SLOTS_BY_ID[slot].get('end_time'),
            }
        user_slot_list = user_slots.items()
        user_slot_list.sort(key=lambda (k, d): (d['calories'], d['session_count'],), reverse=True)
        top_slots_by_user[user] = user_slot_list
    # FORMAT = {'user_id': [(slot_id, {dict(session_count, calories, start_time, end_time)})]
    return top_slots_by_user


def get_user_details(user_ids):
    get_user_query = """SELECT weight, height, dob, gender, user_id FROM t_user WHERE user_id IN (%s)""" % ",".join(map(str, user_ids))
    return {user['user_id']: user for user in Db.execute_select_query(get_user_query)}


def get_required_minutes_for_workout(goals):
    goal_ids = [goal['id'] for goal in goals]
    required_calories_per_goal = get_required_calories_per_day_for_goals(goal_ids)
    user_details = get_user_details([goal['user_id'] for goal in goals])
    print required_calories_per_goal
    print user_details


def get_goals_by_user_with_required_calories_per_day():
    goals = Goal.get_user_goals(date.today(), Util.get_past_date(15))
    goal_ids = [goal['id'] for goal in goals]
    if goal_ids:
        required_calories_per_goal_per_day = get_required_calories_per_day_for_goals(goal_ids)
        print required_calories_per_goal_per_day
        goals_by_user = dict()
        # print goals
        for goal in goals:
            if goal['user_id'] not in goals_by_user:
                goals_by_user[goal['user_id']] = [goal]
            else:
                goals_by_user.get(goal['user_id']).append(goal)

        # print goals_by_user

if __name__ == "__main__":
    # get_top_time_slots_for_users()
    get_goals_by_user_with_required_calories_per_day()
