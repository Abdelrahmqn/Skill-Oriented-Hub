import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///e_learning.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = 'noreply@demo.com'

    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'pic3promo@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'ukns hlfx kixi ydxq')
