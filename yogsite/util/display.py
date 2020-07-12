from datetime import datetime, timedelta
import humanize

def readable_time_delta(dt):

    if dt > datetime.utcnow():
        return humanize.naturaltime(dt, future=True)
    
    return humanize.naturaltime(dt)
