from datetime import datetime, date, timedelta
import humanize

def readable_time_delta(dt):

    if isinstance(dt, date):
        dt = datetime(dt.year, dt.month, dt.day)

    if dt > datetime.utcnow():
        return humanize.naturaltime(dt, future=True)
    
    return humanize.naturaltime(dt)
