import sys, os, logging
logging.basicConfig(stream=sys.stderr)

PROJECT_DIR = '/var/www/www.playlistdepressionscore.com'

# activate_this = f'{PROJECT_DIR}/env/bin/activate'
# with open(activate_this) as file_:
#     exec(file_.read(), dict(__file__=activate_this))
#
sys.path.insert(0, PROJECT_DIR)

from app import app as application
