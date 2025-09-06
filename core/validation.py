from core.spamfilter import normalize_punctuation, is_valid_text

def validate_input_text(text, max_length=200):
    """Validate and normalize input text"""
    if not text or not text.strip():
        raise ValueError("請輸入文字訊息")
    
    # Normalize text
    normalized_text = normalize_punctuation(text)
    
    # Check length
    if len(normalized_text) > max_length:
        raise ValueError(f"請將問題縮短至{max_length}字以內")
    
    # Check if valid Chinese text
    if not is_valid_text(normalized_text):
        raise ValueError("請用中文輸入台灣法律相關問題")
    
    return normalized_text