
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
    判斷單一字元是否為中文字
    根據 Unicode 編碼，常見中文字符範圍為 \u4e00 到 \u9fff
    """
    return '\u4e00' <= ch <= '\u9fff'

def is_valid_text(text: str, threshold: float = 0.2) -> bool:
    """
    檢查訊息是否符合規則：
    去除空格後，非中文字（包括標點符號、數字、英文字母等）不能超過全文長度的 threshold (預設15%)
    
    此處先進行標點符號標準化，以避免因全形與半形標點不一致而影響計算。
    
    參數：
        text: 要檢查的文字訊息
        threshold: 非中文字比例的上限（預設為 0.2，即20%）
        
    回傳：
        True 代表符合規則（訊息有效）
        False 代表不符合規則（垃圾訊息）
    """
    # 標點符號標準化
    normalized_text = normalize_punctuation(text)
    # 移除所有空格
    text_no_spaces = normalized_text.replace(" ", "").replace("\n", "")

    total_len = len(text_no_spaces)
    non_chinese_count = 0
    
    # 計算每個字元中非中文字的數量
    for ch in text_no_spaces:
        if not is_chinese(ch):
            non_chinese_count += 1

    # 計算非中文字比例
    ratio = non_chinese_count / total_len
    return ratio <= threshold

if __name__ == "__main__":
    # 測試範例
    samples = [
        "Sadjlmcnefle12  39481",
        "())()(  ))",
        "[8558675587]",
        "阿阿阿阿  阿阿",
        "Ｈｅｌｌｏ，　世界！"  # 全形英文字及標點
    ]
    for s in samples:
        normalized = normalize_punctuation(s)
        valid = is_valid_text(s)
        print(f"原始文字: {s}")
        print(f"標準化後: {normalized}")
        print(f"是否有效: {valid}\n")
