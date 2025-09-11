

def normalize_punctuation(text: str) -> str:
    """
    Normalize punctuation by converting full-width characters to half-width characters.
    This helps to ensure consistent representation of text across different systems.
    """
    # replace all carriage returns to a single space
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    normalized = []
    for ch in text:
        code = ord(ch)
        # turn full-width space into half-width space
        if code == 12288:
            code = 32
        # turn full-width characters into half-width characters
        elif 65281 <= code <= 65374:
            code -= 65248
        normalized.append(chr(code))
    return ''.join(normalized)

def is_chinese(ch: str) -> bool:
    """
    check if a character is a Chinese character
    unicode range: \u4e00 to \u9fff (CJK Unified Ideographs)
    """
    return '\u4e00' <= ch <= '\u9fff'

def is_valid_text(text: str, threshold: float = 0.2) -> bool:
    """
    check if the text is valid based on the ratio of non-Chinese characters
    threshold: maximum allowed ratio of non-Chinese characters

    """

    # remove all spaces for ratio calculation
    text_no_spaces = text.replace(" ", "")

    total_len = len(text_no_spaces)
    if total_len == 0:
        return False
    non_chinese_count = 0

    # 計算每個字元中非中文字的數量
    for ch in text_no_spaces:
        if not is_chinese(ch):
            non_chinese_count += 1

    # 計算非中文字比例
    ratio = non_chinese_count / total_len
    return ratio <= threshold



def validate_input_text(text, max_length=200):
    """Validate and normalize input text"""
    if not text or not text.strip():
        return '請輸入文字訊息'
    
    # Normalize text
    normalized_text = normalize_punctuation(text)
    
    # Check length
    if len(normalized_text) > max_length:
        return '請將問題縮短至{max_length}字以內'.format(max_length=max_length)
    
    # Check if valid Chinese text
    if not is_valid_text(normalized_text):
        return '請用中文輸入台灣法律相關問題'
    
    else:
        return normalized_text