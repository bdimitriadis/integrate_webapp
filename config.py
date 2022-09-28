import os

class Config(object):
    DEBUG = False
    TESTING = False
    # DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = os.urandom(32)
    WTF_CSRF_TIME_LIMIT = None

class ProductionConfig(Config):
    # DATABASE_URI = 'mysql://user@localhost/foo'
    BACKEND_SERVER = <production_backend_server_ip>
    PN_DECRYPT_KEY = <production_partner_notification_decrypt_key>
    PN_SERVICES_SERVER = <production_partner_notification_services_server_ip>
    GOOGLE_API_KEY = <google_api_key>

class DevelopmentConfig(Config):
    DEBUG = True
    BACKEND_SERVER = <development_backend_server_ip>
    PN_DECRYPT_KEY = <development_partner_notification_decrypt_key>
    PN_SERVICES_SERVER = <development_partner_notification_services_server_ip>
    GOOGLE_API_KEY = <google_api_key>

class TestingConfig(Config):
    TESTING = True
