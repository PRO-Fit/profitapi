from flask.ext.restful import Resource
from flask.ext.restful import abort

from app.common.errors import error_enum
from app.models.analytics import Analytics


class AnalyticsController(Resource):

    def get(self, user_id):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)
        return {
            'day': Analytics.get_present_day_analytics(user_id),
            'week': Analytics.get_present_week_analytics(user_id),
            'month': Analytics.get_last_30_days_analytics(user_id)
        }
