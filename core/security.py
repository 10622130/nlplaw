import hmac
import hashlib
import base64
from flask import current_app

def validate_signature(body, signature):
    """
    驗證簽名是否有效
    """
    try:
        # get Channel Secret from config
        channel_secret = current_app.config['CHANNEL_SECRET']
        # Hash the body using HMAC-SHA256 with the channel secret
        hash = hmac.new(channel_secret.encode('utf-8'),
                        body,  
                        hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash).decode('utf-8')  # decode bytes to str

        # Use hmac.compare_digest for secure comparison
        if hmac.compare_digest(expected_signature, signature):
            return True
        else:
            current_app.logger.error(f"Expected Signature: {expected_signature}, Received: {signature}")
            return False
    except Exception as e:
        current_app.logger.error(f"Error during signature validation: {e}")
        return False