from datetime import timezone, datetime
from api.flask_app.models.database import db


class ProcessedEvent(db.Model):
    __tablename__ = 'processed_events'

    webhook_event_id = db.Column(db.String(50), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @classmethod
    def exists(cls, webhook_event_id: str) -> bool:
        return db.session.get(cls, webhook_event_id) is not None

    @classmethod
    def record(cls, webhook_event_id: str) -> None:
        db.session.add(cls(webhook_event_id=webhook_event_id))
        db.session.commit()
