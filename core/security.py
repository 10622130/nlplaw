import hmac
import hashlib
import base64
from flask import current_app

def validate_signature(body, signature):
    """
    驗證簽名是否有效
    """
    try:
        # 從 current_app.config 取得 Channel Secret
        channel_secret = current_app.config['CHANNEL_SECRET']
        # 使用 Channel Secret 和 body 計算簽名 
        hash = hmac.new(channel_secret.encode('utf-8'),
                        body,  
                        hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash).decode('utf-8')  # byte data 轉成 string

        # 使用 hmac.compare_digest() 進行安全比較
        if hmac.compare_digest(expected_signature, signature):
            return True
        else:
            current_app.logger.error(f"Expected Signature: {expected_signature}, Received: {signature}")
            return False
    except Exception as e:
        current_app.logger.error(f"Error during signature validation: {e}")
        return False