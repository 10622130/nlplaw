"""models/*.py — SQLAlchemy models against the temp-file SQLite DB.

This file also exercises the DB fixture architecture itself (app_context,
db_session, _clean_db row-wiping) early, since every later test file depends
on it working correctly.
"""
import pytest
from sqlalchemy.exc import IntegrityError

from api.flask_app.models import ExamSession, ProcessedEvent, User, UserInput, db


class TestUser:
    def test_exists_is_false_for_unknown_user(self, app_context):
        assert User.exists("Unonexistent") is False

    def test_create_then_exists_is_true(self, app_context):
        User.create("Ucreated001")
        assert User.exists("Ucreated001") is True

    def test_create_sets_timestamps(self, app_context):
        user = User.create("Utimestamps001")
        assert user.created_at is not None
        assert user.updated_at is not None


class TestUserInput:
    def test_create_row_with_fk_to_existing_user(self, app_context, make_user):
        user_id = make_user()
        row = UserInput(user_id=user_id, input_text="請問租屋問題", ai_response="這是回答")
        db.session.add(row)
        db.session.commit()

        assert row.id is not None
        assert row.user_id == user_id
        assert row.input_text == "請問租屋問題"
        assert row.ai_response == "這是回答"

    def test_ai_response_is_nullable(self, app_context, make_user):
        user_id = make_user()
        row = UserInput(user_id=user_id, input_text="問題", ai_response=None)
        db.session.add(row)
        db.session.commit()

        assert row.ai_response is None


class TestProcessedEvent:
    def test_exists_is_false_for_unknown_id(self, app_context):
        assert ProcessedEvent.exists("evt-unknown") is False

    def test_record_then_exists_is_true(self, app_context):
        ProcessedEvent.record("evt-001")
        assert ProcessedEvent.exists("evt-001") is True

    def test_recording_same_id_twice_raises_integrity_error(self, app_context):
        # Documents why linebot_bp._handle_event must call exists() BEFORE
        # record() — a second record() for the same webhook event id hits
        # the primary key constraint at the DB level.
        ProcessedEvent.record("evt-dup")
        with pytest.raises(IntegrityError):
            ProcessedEvent.record("evt-dup")
        db.session.rollback()


class TestExamSession:
    def test_get_answer_is_none_when_unset(self, app_context, make_user):
        user_id = make_user()
        assert ExamSession.get_answer(user_id) is None

    def test_set_then_get_answer_returns_stored_answer(self, app_context, make_user):
        user_id = make_user()
        ExamSession.set(user_id, "B")
        assert ExamSession.get_answer(user_id) == "B"

    def test_set_twice_updates_in_place_without_duplicate_row(self, app_context, make_user):
        user_id = make_user()
        ExamSession.set(user_id, "A")
        ExamSession.set(user_id, "C")

        assert ExamSession.get_answer(user_id) == "C"
        count = db.session.query(ExamSession).filter_by(user_id=user_id).count()
        assert count == 1

    def test_clear_removes_the_row(self, app_context, make_user):
        user_id = make_user()
        ExamSession.set(user_id, "D")
        ExamSession.clear(user_id)
        assert ExamSession.get_answer(user_id) is None

    def test_clear_on_unset_user_is_a_noop(self, app_context, make_user):
        user_id = make_user()
        ExamSession.clear(user_id)  # should not raise
        assert ExamSession.get_answer(user_id) is None
