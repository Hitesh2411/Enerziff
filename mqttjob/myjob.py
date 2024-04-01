
from apscheduler.schedulers.background import BackgroundScheduler

from Myapp.views import c2bPaymentCheck,checking
# from Myapp.views import usedHistory

def c2bPaymentCheck2():
   c2bPaymentCheck()
   # checking()


def start():
    scheduler=BackgroundScheduler()
    scheduler.add_job(c2bPaymentCheck2,'interval',seconds=10)
    scheduler.start()
def checking2():
       scheduler=BackgroundScheduler()
       scheduler.add_job(checking,'interval',seconds=10)
       scheduler.start()


