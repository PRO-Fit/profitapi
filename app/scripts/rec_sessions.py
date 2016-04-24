from app.common.util import Util
from datetime import datetime, timedelta
from app.models.activity import Activity
from app.scripts.test_data import input
import math

# back up code
def get_rec_session():

    MAX_LENGTH = 60
    for user, days in input.iteritems():
        result = []
        lst_pre_act = Activity.get_activity_by_priority(user)
        pref_activity = lst_pre_act[0]
        global done
        for day in days:
            session = {"user_id": user, "start_datetime": "", "end_datetime": "", "session_type": "NOT_NOTIFIED"}
            today = day.get("date")[:10]
            fslots = day.get("free_slots")
            rslots = day.get("rec_slots")
            done = False
            c_session = day.get("existing_session")

            # if existing session is available for the day
            if c_session:
                s_start = Util.convert_string_to_datetime(c_session.get('start_time'))
                s_end = Util.convert_string_to_datetime(c_session.get('end_time'))
                s_length = (s_end - s_start).seconds/60

                given_length = math.floor(day.get("duration").get(pref_activity))

                # TODO: add logic to check the max length of session

                delta = s_length + (given_length - s_length)
                new_end = s_start + timedelta(minutes=delta)

                # check for free slots if it contains the slot
                for slot in fslots:

                    tmp_st = Util.convert_string_to_datetime(today+" "+slot.get('start'))
                    tmp_end = Util.convert_string_to_datetime(today+" "+slot.get('end'))

                    if s_start >= tmp_st and new_end <= tmp_end:
                        session["start_datetime"] = str(s_start)
                        session["end_datetime"] = str(new_end)

                        # TODO: add session to database
                        result.append({day.get("date")[:10]: session})
                        done = True
                        break

            # if existing session is not available for the day
            else:
                # per rec session check conflict with available slots
                global done
                done = False
                for rec_session in rslots:
                    if done:
                        break
                    for a_session in fslots:
                        latest_start = max(Util.convert_string_to_datetime(today+" "+rec_session.get("start")),
                                           Util.convert_string_to_datetime(today+" "+a_session.get("start")))

                        earliest_end = min(Util.convert_string_to_datetime(today+" "+rec_session.get("end")),
                                           Util.convert_string_to_datetime(today+" "+a_session.get("end")))

                        temp_overlap = (earliest_end - latest_start).seconds/60
                        act_length = math.floor(day.get("duration").get(pref_activity))

                        if temp_overlap >= act_length:
                            session["start_datetime"] = str(latest_start)
                            session["end_datetime"] = str(latest_start + timedelta(minutes=act_length))
                            result.append({day.get("date")[:10]: session})
                            done = True
                            break

                for free_session in fslots:
                    free_session

        print result

get_rec_session()
