from dotenv import load_dotenv
import os

load_dotenv()
class Config:
    # Basic Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///e_learning.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = 'noreply@demo.com'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'pic3promo@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'ukns hlfx kixi ydxq')

    # Paymob API configuration
    PAYMOB_ENDPOINT = os.getenv('PAYMOB_ENDPOINT', 'https://accept.paymob.com')
    PAYMOB_INTEGRATION_ID = os.getenv('PAYMOB_INTEGRATION_ID', '1001147')  # Your Merchant ID
    PAYMOB_API_KEY = os.getenv('PAYMOB_API_KEY', 'ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRBd01URTBOeXdpYm1GdFpTSTZJbWx1YVhScFlXd2lmUS5rWkVHR1h1QkxzQ2hqM213d19QSGZ5VnF1bk9LM093SFRJSWoxM29QUTBjR3NGYUtrR3lqWDNRNGszTFU3amd6bmtmclcxYklXemtURXBzVXJEdkVkdw==')
    PAYMOB_SECRET_KEY = os.getenv('PAYMOB_SECRET_KEY', 'egy_sk_live_2c467be5a61bafee482d719dbddb72ac72b8b320dca06ff2de2f935f4e953e88')
    PAYMOB_PUBLIC_KEY = os.getenv('PAYMOB_PUBLIC_KEY', 'egy_pk_live_03USprrdEW0wYLBBQN5p3mQZocGnEOJy')
    PAYMOB_HMAC = os.getenv('PAYMOB_HMAC', 'C78FFDD613FC1FBDDF6C51B74EEE1B78')
