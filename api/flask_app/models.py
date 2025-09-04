from flask_sqlalchemy import SQLAlchemy
from datetime import timezone, datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True)  # Distinct user ID
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def exists(cls, user_id):
        """
        check if user_id exists in the database
        :param user_id: the user id to check, True if exists, False otherwise
        """
        return cls.query.filter_by(id=user_id).first() is not None

class UserInput(db.Model):
    __tablename__ = 'user_inputs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=True)  # 儲存ai回覆
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
