import operator
import copy
from datetime import date
from app.common.database import Db
from app.models.goals import Goal
from app.models.sessions import SessionModel
from app.common.util import Util
from datetime import datetime, timedelta
from app.models.activity import Activity
import math
import json
from app.scripts.calculate_activity_calories_burnt import CaloriesUtil

TIME_SLOTS = Db.execute_select_query("SELECT * FROM t_time_slots_to_recommend ORDER BY popularity ASC")
TIME_SLOTS_BY_ID = {slot['id']: slot for slot in TIME_SLOTS}

DAYS_TO_RECOMMEND = 15

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
                tg.id,
                CASE
                    WHEN tg.start_datetime <= CURRENT_DATE THEN ABS(TRUNCATE((target_burn_calories - gc.calories_burnt)/DATEDIFF(tg.end_datetime, CURRENT_DATE),2))
                    ELSE ABS(TRUNCATE((target_burn_calories - gc.calories_burnt)/DATEDIFF(tg.end_datetime, tg.start_datetime),2))
                END as cal_per_day
                FROM t_goal tg
                INNER JOIN
                (
                    SELECT tg.id,
                    CASE
                        WHEN SUM(calories_burnt) IS NULL THEN 0
                        ELSE SUM(calories_burnt)
                    END as calories_burnt
                    FROM t_goal tg
                    LEFT JOIN t_goal_activity tga ON tg.id = tga.goal_id
                    LEFT JOIN t_user_activity ta ON tga.activity_id = ta.id
                    WHERE tg.id IN (%s)
                    GROUP BY tg.id
                ) gc
                ON tg.id = gc.id
    """
    return {goal.get('id'): goal.get('cal_per_day') for goal in Db.execute_select_query(query % ",".join(map(str, goal_ids)))}


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
                'start': str(TIME_SLOTS_BY_ID[slot].get('start_time')),
                'end': str(TIME_SLOTS_BY_ID[slot].get('end_time')),
            }
        user_slot_list = user_slots.items()
        user_slot_list.sort(key=lambda (k, d): (d['calories'], d['session_count'],), reverse=True)
        for id, dict in user_slot_list:
            dict.pop('calories')
            dict.pop('session_count')
        top_slots_by_user[user] = user_slot_list
    # FORMAT = {'user_id': [(slot_id: {dict(session_count, calories, start_time, end_time))]
    return top_slots_by_user


def get_user_details_by_user_id(user_ids):
    get_user_query = """SELECT DISTINCT weight, height, dob, gender, user_id FROM t_user WHERE user_id IN ('%s')""" % "', '".join(map(str, user_ids))
    return {user['user_id']: user for user in Db.execute_select_query(get_user_query)}


def get_required_minutes_for_workout_per_day_by_goal():
    goals = Goal.get_user_goals(date.today(), Util.get_future_date(DAYS_TO_RECOMMEND))
    goal_ids = [goal['id'] for goal in goals]
    reqd_calories_per_day_by_goal_id = get_required_calories_per_day_for_goals(goal_ids)
    users_by_user_id = get_user_details_by_user_id([goal['user_id'] for goal in goals])
    reqd_minutes_per_day_by_goal_id = dict()
    for goal in goals:
        user = users_by_user_id[goal['user_id']]
        duration = CaloriesUtil.get_time_in_minutes_to_burn_calories(
            reqd_calories_per_day_by_goal_id[goal['id']],
            user['weight'],
            user['height'],
            CaloriesUtil.calculate_age(user['dob']),
            user['gender']
        )
        reqd_minutes_per_day_by_goal_id[str(goal['id'])] = {
            'user_id': user['user_id'],
            'duration': duration,
            'start_date': goal['start_datetime'] if goal['start_datetime'] > Util.get_current_datetime() else
            Util.get_current_datetime(),
            'end_date': goal['end_datetime'] if goal['end_datetime'] < Util.get_future_date(DAYS_TO_RECOMMEND) else Util.get_future_date(15)
        }
    return reqd_minutes_per_day_by_goal_id


def append_popular_slots(user_slots):
    user_slots_dict = dict(user_slots)
    for slot in TIME_SLOTS:
        if len(user_slots) == 5:
            break
        slotc = copy.deepcopy(slot)
        slotc.pop('popularity')
        slotc.pop('id')
        if slot['id'] not in user_slots_dict:
            user_slots.append((slot['id'], {'start': str(slotc['start_time']), 'end': str(slotc['end_time'])}))
    return user_slots


def get_user_free_rec_slots():
    time_slots_by_user_id = get_top_time_slots_for_users()
    reqd_mins_by_goal_id = get_required_minutes_for_workout_per_day_by_goal()
    output_by_user_id = dict()
    for goal_id, metadata in reqd_mins_by_goal_id.iteritems():
        user_data_list = []
        free_slots = SessionModel.get_free_slots(
            metadata['user_id'],
            metadata['start_date'].strftime("%Y-%m-%d"),
            metadata['end_date'].strftime("%Y-%m-%d")
        )
        rec_slots = append_popular_slots(time_slots_by_user_id[metadata['user_id']]) \
            if metadata['user_id'] in time_slots_by_user_id \
            else append_popular_slots([])
        for date, slots in free_slots.iteritems():
            existing_session = SessionModel.get_user_sessions_in_duration(
                    datetime.strptime(date, '%Y-%m-%d %H:%M:%S'),
                    datetime.strptime(date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=23, minutes=59, seconds=59),
                    metadata['user_id'])
            data = {
                'date': date,
                'duration': metadata['duration'],
                'free_slots': slots,
                'rec_slots': dict(rec_slots).values(),
                'existing_session': existing_session if existing_session else None
            }
            user_data_list.append(data)
        if metadata['user_id'] in output_by_user_id:
            output_by_user_id[metadata['user_id']] += user_data_list
        else:
            output_by_user_id[metadata['user_id']] = user_data_list
    return output_by_user_id


def get_rec_sessions():
    input = get_user_free_rec_slots()
    act_type = Activity.get_activity_type()
    MAX_LENGTH = 45
    for user, days in input.iteritems():
        result = []
        lst_pre_act = Activity.get_activity_by_priority(user)
        pref_activity = lst_pre_act[0]
        global done
        for day in days:

            session = {"user_id": user, "start_datetime": "", "end_datetime": "", "session_status": "NOT_NOTIFIED",
                       "name": "Smart Session", "session_feedback_id": 0, "workout_type_id": act_type.get(pref_activity) }

            today = day.get("date")[:10]
            fslots = day.get("free_slots")
            rslots = day.get("rec_slots")
            done = False
            c_session = day.get("existing_session")

            # if existing session is available for the day
            if c_session:
                c_session = c_session[0]
                s_start = c_session.get('start_datetime')
                s_end = c_session.get('end_datetime')
                s_length = (s_end - s_start).seconds/60

                given_length = math.floor(day.get("duration").get(pref_activity))

                delta = s_length + (given_length - s_length)
                if(delta > MAX_LENGTH):
                    new_end = s_start + timedelta(minutes=MAX_LENGTH)
                else:
                    new_end = s_start + timedelta(minutes=delta)

                # check for free slots if it contains the slot
                for slot in fslots:

                    tmp_st = Util.convert_string_to_datetime(today+" "+slot.get('start'))
                    tmp_end = Util.convert_string_to_datetime(today+" "+slot.get('end'))

                    if s_start >= tmp_st and new_end <= tmp_end:
                        session["start_datetime"] = str(s_start)
                        session["end_datetime"] = str(new_end)
                        
                        SessionModel.update_session(user, str(c_session.get("id")), session)
                        result.append({day.get("date")[:10]: session})
                        done = True
                        break

            # if existing session is not available for the day
            else:
                # per rec session check conflict with available slots
                done = False
                for rec_session in rslots:
                    for a_session in fslots:
                        latest_start = max(Util.convert_string_to_datetime(today+" "+rec_session.get("start")),
                                           Util.convert_string_to_datetime(today+" "+a_session.get("start")))

                        earliest_end = min(Util.convert_string_to_datetime(today+" "+rec_session.get("end")),
                                           Util.convert_string_to_datetime(today+" "+a_session.get("end")))

                        temp_overlap = (earliest_end - latest_start).seconds/60
                        act_length = math.floor(day.get("duration").get(pref_activity))

                        if temp_overlap >= act_length or temp_overlap >= MAX_LENGTH:
                            session["start_datetime"] = str(latest_start)
                            if act_length> MAX_LENGTH:
                                session["end_datetime"] = str(latest_start + timedelta(minutes=MAX_LENGTH))
                            else:
                                session["end_datetime"] = str(latest_start + timedelta(minutes=act_length))

                            # TODO: add session to database
                            SessionModel.insert_user_session(user, session)
                            result.append({day.get("date")[:10]: session})
                            done = True
                            break

                    if done:
                        break

        print json.dumps(result)

if __name__ == "__main__":
    get_rec_sessions()
