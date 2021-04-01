from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

flask_db_ext = SQLAlchemy() # the fact that mankind is so far behind that I have to do this is sad
flask_limiter_ext = Limiter(
	key_func = get_remote_address
)