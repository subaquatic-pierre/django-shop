

import os


class Config():

    SECRET_KEY = "somesupersecretkey"
    DEBUG = True
    DEVELOPMENT = False
    DB_NAME = "SET_ENVIRON_VARIABLE"
    DB_USER = "SET_ENVIRON_VARIABLE"
    DB_PASSWORD = "SET_ENVIRON_VARIABLE"
    DB_HOST = "SET_ENVIRON_VARIABLE"
    STRIPE_LIVE_PUBLIC_KEY = "SET_ENVIRON_VARIABLE"
    STRIPE_LIVE_SECRET_KEY = "SET_ENVIRON_VARIABLE"
    EMAIL_HOST_USER = "SET_ENVIRON_VARIABLE@USER.COM"
    EMAIL_HOST_PASSWORD = "SET_ENVIRON_VARIABLE"
