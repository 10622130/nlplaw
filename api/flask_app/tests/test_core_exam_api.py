"""core/exam_api.py — exam question fetch over HTTP."""
import pytest
import requests

from core.exam_api import get_random_question
from helpers import make_requests_response_mock


class TestGetRandomQuestion:
    def test_success_returns_parsed_json(self, mocker):
        mock_resp = make_requests_response_mock(
            json_data={"question": "民法上的不當得利是什麼？", "answer": "B"}
        )
        post = mocker.patch("core.exam_api.requests.post", return_value=mock_resp)

        result = get_random_question("112 民法、民事訴訟法", "http://mock-exam.test/random-question")

        assert result == {"question": "民法上的不當得利是什麼？", "answer": "B"}
        _, kwargs = post.call_args
        assert kwargs["json"] == {"year_subject": "112 民法、民事訴訟法"}
        assert kwargs["timeout"] == 10

    def test_http_error_propagates(self, mocker):
        mock_resp = make_requests_response_mock(
            raise_for_status_effect=requests.HTTPError("500 Server Error")
        )
        mocker.patch("core.exam_api.requests.post", return_value=mock_resp)

        with pytest.raises(requests.HTTPError):
            get_random_question("112 民法、民事訴訟法", "http://mock-exam.test/random-question")
