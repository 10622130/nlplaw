import re
from flask import current_app
from api.flask_app.models import db, ExamSession
from core.exam_api import get_random_question
from core.line_api import send_reply_messages, text_message, text_with_quick_reply

SUBJECTS = [
    "民法、民事訴訟法",
    "刑法、刑事訴訟法、法律倫理",
    "憲法、行政法、國際公法、國際私法",
    "公司法、保險法、票據法、證券交易法、強制執行法、法學英文",
]
YEARS = ["112", "111", "110", "109", "108", "107", "106", "105", "104", "103"]
OPTIONS = {"A", "B", "C", "D"}

SUBJECT_RE = re.compile(
    r'^(' + '|'.join(re.escape(s) for s in SUBJECTS) + r')$'
)
YEAR_SUBJECT_RE = re.compile(
    r'^(10[3-9]|11[0-2])\s+(' + '|'.join(re.escape(s) for s in SUBJECTS) + r')$'
)


def handle_subject_selection(subject: str, reply_token: str) -> None:
    """Show year quick reply buttons for the selected subject."""
    msg = text_with_quick_reply(
        text='請選擇要練習的年份',
        buttons=[(f"{y}年", f"{y} {subject}") for y in YEARS],
    )
    _send([msg], reply_token)


def handle_year_subject(user_id: str, year_subject: str, reply_token: str) -> None:
    """Fetch a question, persist the answer, and send the question with A/B/C/D."""
    try:
        exam = get_random_question(year_subject, current_app.config['EXAM_API_URL'])
    except Exception as e:
        current_app.logger.error(f"Exam API error: {e}")
        _send([text_message("題目取得失敗，請稍後再試。")], reply_token)
        return

    question = exam.get('question', '')
    answer = exam.get('answer', '')

    ExamSession.set(user_id, answer)

    question_msg = text_with_quick_reply(
        text=question,
        buttons=[(opt, opt) for opt in ["A", "B", "C", "D"]],
    )
    _send([question_msg], reply_token)


def handle_answer(user_id: str, choice: str, reply_token: str) -> None:
    """Compare choice against stored answer and reply with result."""
    correct = ExamSession.get_answer(user_id)
    ExamSession.clear(user_id)

    if correct is None:
        _send([text_message("目前沒有待作答的題目，請先選擇科目與年份。")], reply_token)
        return

    if choice == correct:
        result = "恭喜你答對了！"
    else:
        result = f"答錯了⋯答案是 {correct}"

    _send([text_message(result)], reply_token)


def _send(messages: list[dict], reply_token: str) -> None:
    from core.line_api import send_reply_messages
    response, status = send_reply_messages(
        current_app.config['CHANNEL_ACCESS_TOKEN'], reply_token, messages
    )
    if status != 200:
        current_app.logger.error(f"LINE reply failed: {status} {response.text}")
