from os import getenv

def generate_payment_url(token):
    """ payment url generator
        ==========
        Return:
            urls dynamicly
    """
    frame_id = getenv('PAYMOB_IFRAME_ID')
    return f"https://accept.paymob.com/api/acceptance/iframes/{frame_id}?payment_token={token}"
