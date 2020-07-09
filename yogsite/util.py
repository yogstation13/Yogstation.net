from datetime import datetime, timedelta
from functools import wraps
import humanize
from flask import redirect, session

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

# Decorator to block someone from viewing a page unless they are logged in as an admin
def login_required(view):
    @wraps(view)

    def decorated_function(*args, **kwargs):
        if "ckey" not in session:
            return redirect("/login")

        return view(*args, **kwargs)

    return decorated_function