"""core/spamfilter.py — pure functions, no mocking or app context needed."""
from core.spamfilter import (
    is_chinese,
    is_valid_text,
    normalize_punctuation,
    validate_input_text,
)


class TestNormalizePunctuation:
    def test_full_width_digits_and_punctuation_become_half_width(self):
        # Only U+FF01-FF5E (Halfwidth/Fullwidth Forms) is converted here —
        # CJK Symbols and Punctuation (e.g. "。" U+3002) is a different
        # Unicode block and is left untouched by this function.
        assert normalize_punctuation("１２３，！") == "123,!"

    def test_full_width_space_becomes_half_width_space(self):
        assert normalize_punctuation("中　文") == "中 文"

    def test_crlf_cr_lf_become_single_space(self):
        assert normalize_punctuation("中\r\n文\r文\n文") == "中 文 文 文"

    def test_ascii_text_passes_through_unchanged(self):
        assert normalize_punctuation("hello, world!") == "hello, world!"


class TestIsChinese:
    def test_chinese_character_is_true(self):
        assert is_chinese("中") is True

    def test_ascii_letter_is_false(self):
        assert is_chinese("a") is False

    def test_lower_boundary_u4e00_is_true(self):
        assert is_chinese("一") is True

    def test_upper_boundary_u9fff_is_true(self):
        assert is_chinese("鿿") is True

    def test_just_below_lower_boundary_is_false(self):
        assert is_chinese("䷿") is False

    def test_just_above_upper_boundary_is_false(self):
        assert is_chinese("ꀀ") is False


class TestIsValidText:
    def test_empty_string_is_invalid(self):
        assert is_valid_text("") is False

    def test_pure_chinese_is_valid(self):
        assert is_valid_text("這是一個法律問題") is True

    def test_mixed_within_threshold_is_valid(self):
        # 1 non-Chinese char out of 9 -> ratio ~0.11 <= 0.2
        assert is_valid_text("這是一個法律問題a") is True

    def test_mixed_exceeding_threshold_is_invalid(self):
        # 3 non-Chinese chars out of 4 -> ratio 0.75 > 0.2
        assert is_valid_text("中abc") is False

    def test_spaces_are_excluded_from_ratio(self):
        assert is_valid_text("中  文") is True


class TestValidateInputText:
    def test_empty_string_is_invalid(self):
        assert validate_input_text("") == (False, "請輸入文字訊息")

    def test_whitespace_only_is_invalid(self):
        assert validate_input_text("   ") == (False, "請輸入文字訊息")

    def test_valid_chinese_text_returns_normalized(self):
        # The full-width "？" (U+FF1F) IS in the normalized range, so it
        # becomes half-width "?" in the returned text.
        is_valid, result = validate_input_text("請問租屋糾紛該怎麼處理？")
        assert is_valid is True
        assert result == "請問租屋糾紛該怎麼處理?"

    def test_text_exceeding_default_max_length_is_invalid(self):
        text = "法" * 201
        assert validate_input_text(text) == (False, "請將問題縮短至200字以內")

    def test_text_within_default_max_length_boundary_is_valid(self):
        text = "法" * 200
        is_valid, _ = validate_input_text(text)
        assert is_valid is True

    def test_custom_max_length_is_respected(self):
        text = "法律問題內容"
        assert validate_input_text(text, max_length=5) == (False, "請將問題縮短至5字以內")

    def test_non_chinese_heavy_text_is_invalid(self):
        assert validate_input_text("What is the law here") == (
            False,
            "請用中文輸入台灣法律相關問題",
        )

    def test_full_width_punctuation_is_normalized_before_validation(self):
        # 1 full-width punctuation mark out of 9 chars after normalization
        # keeps the non-Chinese ratio (1/9 ~= 0.11) under the 0.2 threshold.
        is_valid, result = validate_input_text("這是一個問題，對嗎")
        assert is_valid is True
        assert result == "這是一個問題,對嗎"