from datetime import timezone, datetime
from api.flask_app.models.database import db


class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'

    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), primary_key=True)
    correct_answer = db.Column(db.String(1), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @classmethod
    def set(cls, user_id: str, answer: str) -> None:
        """Upsert the correct answer for the user's current question."""
        session = db.session.get(cls, user_id)
        if session:
            session.correct_answer = answer
            session.updated_at = datetime.now(timezone.utc)
        else:
            db.session.add(cls(user_id=user_id, correct_answer=answer))
        db.session.commit()

    @classmethod
    def get_answer(cls, user_id: str) -> str | None:
        session = db.session.get(cls, user_id)
        return session.correct_answer if session else None

    @classmethod
    def clear(cls, user_id: str) -> None:
        session = db.session.get(cls, user_id)
        if session:
            db.session.delete(session)
            db.session.commit()
