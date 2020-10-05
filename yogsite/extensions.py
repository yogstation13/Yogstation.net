from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

flask_db_ext = SQLAlchemy() # the fact that mankind is so far behind that I have to do this is sad

login_manager = LoginManager()