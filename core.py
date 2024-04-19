import sys
import subprocess

def install(package):
    # -i https://pypi.mirrors.ustc.edu.cn/simple/
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    from flask_apscheduler import APScheduler
except:
    install('Flask-APScheduler')
    from flask_apscheduler import APScheduler


scheduler = APScheduler()