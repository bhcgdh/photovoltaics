from os import environ
from flask_script import Server, Manager, Shell
from run import create_app
import json
import datetime
import numpy as np
from bson.objectid import ObjectId
import sys
from flask._compat import text_type
from config import Config
import warnings

warnings.filterwarnings("ignore")

class JsonEncoder(json.JSONEncoder):
    """
    extend json-encoder class
    """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.integer):
            return int(o)

        return json.JSONEncoder.default(self, o)

app = create_app(environ.get('ENVIRONMENT', "default"))

manager = Manager(app=app)

# manager.run重写 方法变参数
def new_run(commands=None, default_command=None):
    if commands:
        manager._commands.update(commands)

    # Make sure all of this is Unicode
    argv = list(text_type(arg) for arg in sys.argv)

    if default_command is not None and len(argv) == 1:
        argv.append(default_command)
    try:
        result = manager.handle(argv[0], ['runserver'])
    except SystemExit as e:
        result = e.code

    sys.exit(result or 0)

def make_shell_context():
    return dict(app=app)


# port = Config.PORT, # 本地端口，后续需要环境中设置
PORT = 2000
manager.add_command('runserver',
                    Server(host='0.0.0.0', 
                           port=PORT,
                           use_debugger=False, 
                           use_reloader=False, 
                           threaded=True))

manager.add_command('shell', 
                    Shell(make_context=make_shell_context))

# manager.run = new_run()
# http://127.0.0.1:5000/pvpowerpredict/documentation
import os
if __name__ == '__main__':
    manager.run(default_command='runserver')


