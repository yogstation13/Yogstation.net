from datetime import datetime, timedelta
import humanize

class Struct():
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [Struct(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, Struct(b) if isinstance(b, dict) else b)


def readable_time_delta(dt):

    if dt > datetime.utcnow():
        return humanize.naturaltime(dt, future=True)
    
    return humanize.naturaltime(dt)