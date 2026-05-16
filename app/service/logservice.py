from app.extensions import db
from app.models import Logging


class LoggingService:
    @staticmethod
    def log_action(
        user_id,
        target_type,
        target_id,
        action,
        reason=None,
        commit=True,
    ):
        if not user_id or not target_type or not action:
            return None

        entry = Logging(
            user_id=int(user_id),
            target_type=str(target_type),
            target_id=int(target_id) if target_id is not None else 0,
            action=str(action),
            reason=reason,
        )
        db.session.add(entry)
        if commit:
            db.session.commit()
        return entry
