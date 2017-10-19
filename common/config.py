import os
from helpers import exec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = exec("cd ~ && pwd")[0][0]
USER = HOME.split('/')[-1]
SERVER_ROOT = "{}/web".format(HOME)