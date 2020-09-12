import os

class Config(object):
    SECRET_KEY = 'dabshdsadahsdkja'
    DATABASE= os.path.join(app.instance_path, 'app.sqlite')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USRNAME = ''
    MAIL_PASSWORD = ''
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    GA_TRACKING_ID = 'UA-000001'
