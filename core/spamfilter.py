def normalize_punctuation(text: str) -> str:
    """
    文字格式標準化
    空格、換行符、標點符號統一轉換

    依據 Unicode 編碼：
    - 全形空白（U+3000）轉為半形空白（U+0020）
    - 全形符號（U+FF01 至 U+FF5E）轉為對應的半形符號
    """
    # 將所有換行符統一轉換為 \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = []
    for ch in text:
        code = ord(ch)
        # 全形空白（U+3000）轉換成普通空格
        if code == 12288:
            code = 32
        # 若字符位於全形字符範圍內，轉換為半形
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
    # 標點符號標準化
    normalized_text = normalize_punctuation(text)
    # 移除所有空格
    text_no_spaces = normalized_text.replace(" ", "").replace("\n", "")

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