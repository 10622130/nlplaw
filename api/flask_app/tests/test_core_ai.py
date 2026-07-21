"""core/ai.py — OpenAI GPT-4o call wrapper.

`client = OpenAI(api_key=...)` sits OUTSIDE the try block (core/ai.py line
10); only the `.chat.completions.create(...)` call and its result handling
are wrapped in try/except. So a failure in `.create()` is swallowed and
returns the Chinese fallback string, but a failure in the `OpenAI(...)`
constructor itself propagates uncaught.
"""
import pytest

from core.ai import get_openai_response
from helpers import make_openai_client_mock


class TestGetOpenaiResponse:
    def test_success_returns_message_content(self, mocker):
        mocker.patch("core.ai.OpenAI", return_value=make_openai_client_mock("這是法律建議"))

        result = get_openai_response("租屋糾紛怎麼辦？", "fake-api-key")

        assert result == "這是法律建議"

    def test_create_call_exception_returns_fallback_string(self, mocker):
        client = make_openai_client_mock("unused")
        client.chat.completions.create.side_effect = RuntimeError("API down")
        mocker.patch("core.ai.OpenAI", return_value=client)

        result = get_openai_response("租屋糾紛怎麼辦？", "fake-api-key")

        assert result == "AI 發生錯誤，請稍後再試。"

    def test_constructor_exception_propagates_uncaught(self, mocker):
        mocker.patch("core.ai.OpenAI", side_effect=ValueError("bad api key format"))

        with pytest.raises(ValueError):
            get_openai_response("租屋糾紛怎麼辦？", "invalid-key")
