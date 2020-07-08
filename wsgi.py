from yogsite import app
from yogsite.config import cfg

if __name__ == "__main__":
	app.run("localhost", port=80, debug=True)