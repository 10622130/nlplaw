from datetime import timezone, datetime
from api.flask_app.models.database import db

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
    
    @classmethod
    def create(cls, user_id):
        """Create new user"""
        user = cls(id=user_id)
        db.session.add(user)
        db.session.commit()
        return user