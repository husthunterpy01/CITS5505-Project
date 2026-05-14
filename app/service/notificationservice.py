from app.extensions import db, socketio
from app.models import Notification


class NotificationService:
    @staticmethod
    def serialize_notification(notification):
        return {
            'notification_id': notification.notification_id,
            'recipient_id': notification.recipient_id,
            'notification_type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'action_url': notification.action_url,
            'reference_type': notification.reference_type,
            'reference_id': notification.reference_id,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat() if notification.created_at else None,
        }

    @staticmethod
    def emit_notification(notification):
        socketio.emit(
            'notification_created',
            NotificationService.serialize_notification(notification),
            room=f'user:{notification.recipient_id}',
        )

    @staticmethod
    def create_notification(
        recipient_id,
        notification_type,
        title,
        message,
        action_url=None,
        reference_type=None,
        reference_id=None,
        commit=True,
    ):
        notification = Notification(
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        db.session.add(notification)
        if commit:
            db.session.commit()
            NotificationService.emit_notification(notification)
        return notification

    @staticmethod
    def get_recent_notifications(recipient_id, limit=20):
        return (
            Notification.query
            .filter_by(recipient_id=recipient_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_unread(recipient_id):
        return Notification.query.filter_by(recipient_id=recipient_id, is_read=False).count()

    @staticmethod
    def mark_read(recipient_id, notification_id):
        notification = Notification.query.filter_by(
            notification_id=notification_id,
            recipient_id=recipient_id,
        ).first()
        if not notification:
            return False
        notification.is_read = True
        db.session.commit()
        return True

    @staticmethod
    def mark_all_read(recipient_id):
        Notification.query.filter_by(recipient_id=recipient_id, is_read=False).update(
            {'is_read': True},
            synchronize_session=False,
        )
        db.session.commit()
