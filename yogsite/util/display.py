from datetime import datetime, date, timedelta
import humanize

def readable_time_delta(dt):
    if not isinstance(dt, datetime) and isinstance(dt, date):
        dt = datetime(dt.year, dt.month, dt.day)

    if dt > datetime.utcnow():
        return humanize.naturaltime(datetime.utcnow()-dt, future=True)
    
    return humanize.naturaltime(datetime.utcnow()-dt)