import secrets

def generate_api_key():
    """生成一個隨機的 API 金鑰"""
    return secrets.token_urlsafe(32)  # 生成一個 32 字元長的隨機 URL 安全字串

if __name__ == "__main__":
    api_key = generate_api_key()
    print(f"Generated API Key: {api_key}")
    # 將生成的 API 金鑰寫入 .env 檔案
    with open('.env', 'a') as f:
        f.write(f"API_KEY={api_key}\n")