from datetime import timezone, datetime
from api.flask_app.models.database import db

class UserInput(db.Model):
    __tablename__ = 'user_inputs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=True)  # 儲存ai回覆
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))