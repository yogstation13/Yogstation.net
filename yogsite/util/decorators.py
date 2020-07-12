from functools import wraps
from flask import redirect, session

# Decorator to block someone from viewing a page unless they are logged in as an admin
def login_required(view):
    @wraps(view)

    def decorated_function(*args, **kwargs):
        if "ckey" not in session:
            return redirect("/login")

        return view(*args, **kwargs)

    return decorated_function