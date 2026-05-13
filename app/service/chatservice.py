from datetime import datetime
from flask import session
from app.extensions import db
from app.models import Conversation, ConversationParticipant, Message, Product, User, Notification
from app.service.notificationservice import NotificationService


class ChatService:
    def __init__(self):
        self.user_sessions = {}

    @staticmethod
    def _error(message):
        return {'ok': False, 'error': message}

    def _get_user_id(self, sid):
        return session.get('user_id') or self.user_sessions.get(sid, {}).get('user_id')

    @staticmethod
    def _find_shared_conversation(user_id, target_user_id):
        user_conv_ids = {
            p.conversation_id
            for p in ConversationParticipant.query.filter_by(user_id=user_id).all()
        }
        target_conv_ids = {
            p.conversation_id
            for p in ConversationParticipant.query.filter_by(user_id=target_user_id).all()
        }
        shared_ids = list(user_conv_ids.intersection(target_conv_ids))
        if not shared_ids:
            return None
        return Conversation.query.filter(Conversation.conversation_id.in_(shared_ids)) \
            .order_by(Conversation.updated_at.desc()) \
            .first()

    @staticmethod
    def _default_product_id():
        first_product = Product.query.order_by(Product.product_id.asc()).first()
        return first_product.product_id if first_product else None

    def register_connection(self, sid):
        try:
            user_id = session.get('user_id')
        except Exception as exc:
            return {'ok': True, 'user_id': None, 'warning': f'Socket connect session read failed: {exc}'}

        if user_id:
            self.user_sessions[sid] = {
                'user_id': user_id,
                'active_conversation_id': None,
            }
        return {'ok': True, 'user_id': user_id}

    def _is_user_online(self, user_id):
        return any(
            session_data.get('user_id') == user_id
            for session_data in self.user_sessions.values()
        )

    def _is_user_viewing_conversation(self, user_id, conversation_id):
        for session_data in self.user_sessions.values():
            if session_data.get('user_id') != user_id:
                continue
            if session_data.get('active_conversation_id') == conversation_id:
                return True
        return False

    def set_active_conversation(self, sid, payload):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        if sid not in self.user_sessions:
            self.user_sessions[sid] = {'user_id': user_id, 'active_conversation_id': None}

        raw_conversation_id = (payload or {}).get('conversation_id')
        if raw_conversation_id in (None, ''):
            self.user_sessions[sid]['active_conversation_id'] = None
            return {'ok': True, 'conversation_id': None}

        try:
            conversation_id = int(raw_conversation_id)
        except (TypeError, ValueError):
            return self._error('Invalid conversation_id')

        is_participant = ConversationParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=user_id,
        ).first()
        if not is_participant:
            return self._error('User not a participant of this conversation')

        self.user_sessions[sid]['active_conversation_id'] = conversation_id
        return {'ok': True, 'conversation_id': conversation_id}

    def mark_notification_read(self, sid, payload):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        raw_notification_id = (payload or {}).get('notification_id')
        if raw_notification_id in (None, ''):
            Notification.query.filter_by(recipient_id=user_id, is_read=False).update(
                {'is_read': True},
                synchronize_session=False,
            )
            db.session.commit()
            return {'ok': True, 'notification_id': None}

        try:
            notification_id = int(raw_notification_id)
        except (TypeError, ValueError):
            return self._error('Invalid notification_id')

        notification = Notification.query.filter_by(
            notification_id=notification_id,
            recipient_id=user_id,
        ).first()
        if not notification:
            return self._error('Notification not found')

        if not notification.is_read:
            notification.is_read = True
            db.session.commit()

        return {'ok': True, 'notification_id': notification_id}

    def unregister_connection(self, sid):
        existed = sid in self.user_sessions
        if existed:
            del self.user_sessions[sid]
        return existed

    def join_conversation(self, sid, payload):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        conversation_id = (payload or {}).get('conversation_id')
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return self._error('Conversation not found')

        related_participants = ConversationParticipant.query \
            .filter_by(conversation_id=conversation.conversation_id) \
            .all()
        if not any(p.user_id == user_id for p in related_participants):
            return self._error('User not a participant of this conversation')

        room = f"conv:{conversation.conversation_id}"
        if sid in self.user_sessions:
            self.user_sessions[sid]['active_conversation_id'] = conversation.conversation_id
        return {'ok': True, 'conversation_id': conversation.conversation_id, 'room': room}

    def load_messages(self, sid, payload):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        conversation_id = (payload or {}).get('conversation_id')
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return self._error('Conversation not found')

        messages = Message.query.filter_by(conversation_id=conversation_id) \
            .order_by(Message.sent_at.desc()) \
            .limit(50) \
            .all()
        if not messages:
            return {'ok': True, 'conversation_id': conversation_id, 'messages': []}

        sender_ids = list({msg.sender_id for msg in messages if msg.sender_id})
        senders = User.query.filter(User.user_id.in_(sender_ids)).all() if sender_ids else []
        sender_map = {user.user_id: f"{user.first_name} {user.last_name}" for user in senders}

        message_list = [{
            'message_id': msg.message_id,
            'sender_id': msg.sender_id,
            'sender_username': sender_map.get(msg.sender_id, f'User {msg.sender_id}'),
            'content': msg.content,
            'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
            'is_read': msg.is_read,
        } for msg in reversed(messages)]

        return {'ok': True, 'conversation_id': conversation_id, 'messages': message_list}

    def send_message(self, sid, payload):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        conversation_id = (payload or {}).get('conversation_id')
        content = ((payload or {}).get('content') or '').strip()
        if not conversation_id or not content:
            return self._error('Missing conversation or message content')

        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return self._error('Conversation not found')

        related_participants = ConversationParticipant.query.filter_by(conversation_id=conversation_id).all()
        if not any(p.user_id == user_id for p in related_participants):
            return self._error('User not a participant of this conversation')

        message = Message(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=content,
            sent_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        try:
            db.session.add(message)
            conversation.updated_at = datetime.utcnow()

            sender = User.query.get(user_id)
            sender_name = f"{sender.first_name} {sender.last_name}" if sender else f'User {user_id}'
            receiver_ids = [
                participant.user_id
                for participant in related_participants
                if participant.user_id != user_id
            ]
            pending_notifications = []
            for receiver_id in receiver_ids:
                if self._is_user_viewing_conversation(receiver_id, conversation_id):
                    continue
                notification = NotificationService.create_notification(
                    recipient_id=receiver_id,
                    notification_type='new_message',
                    title=f'New message from {sender_name}',
                    message=content if len(content) <= 140 else f'{content[:137]}...',
                    action_url='/',
                    reference_type='conversation',
                    reference_id=conversation_id,
                    commit=False,
                )
                pending_notifications.append(notification)

            db.session.commit()
            for notification in pending_notifications:
                NotificationService.emit_notification(notification)
        except Exception as exc:
            db.session.rollback()
            print(f'Failed to commit message for conversation {conversation_id}: {exc}')
            return self._error('Failed to save message. Please try again.')

        return {
            'ok': True,
            'room': f"conv:{conversation_id}",
            'message': {
                'message_id': message.message_id,
                'conversation_id': conversation_id,
                'sender_id': user_id,
                'sender_username': sender_name,
                'content': content,
                'sent_at': message.sent_at.isoformat(),
            },
        }

    def list_conversations(self, sid):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        user = User.query.get(user_id)
        if not user:
            return self._error('User not found')

        out = []
        contacts = User.query.filter(User.user_id != user_id).order_by(User.first_name.asc(), User.last_name.asc()).all()
        for contact in contacts:
            shared_conv = self._find_shared_conversation(user_id, contact.user_id)
            last_msg = None
            if shared_conv:
                last_msg = Message.query.filter_by(conversation_id=shared_conv.conversation_id) \
                    .order_by(Message.sent_at.desc()) \
                    .first()

            out.append({
                'conversation_id': shared_conv.conversation_id if shared_conv else None,
                'product_id': shared_conv.product_id if shared_conv else None,
                'other_participant': {
                    'user_id': contact.user_id,
                    'first_name': contact.first_name,
                    'last_name': contact.last_name,
                    'role': contact.role,
                },
                'last_message_preview': last_msg.content[:30] if last_msg else None,
                'has_history': bool(last_msg),
            })

        return {'ok': True, 'conversations': out}

    def start_conversation(self, sid, payload):
        user_id = self._get_user_id(sid)
        if not user_id:
            return self._error('User not authenticated')

        target_user_id = (payload or {}).get('target_user_id')
        if not target_user_id:
            return self._error('Missing target user')
        try:
            target_user_id = int(target_user_id)
        except (TypeError, ValueError):
            return self._error('Invalid target user')

        if target_user_id == int(user_id):
            return self._error('Cannot start a conversation with yourself')

        target_user = User.query.get(target_user_id)
        if not target_user:
            return self._error('Target user not found')

        current_user = User.query.get(user_id)
        if not current_user:
            return self._error('User not found')

        requested_product_id = (payload or {}).get('product_id')
        if current_user.role == 'standard_user' and target_user.role == 'standard_user' and not requested_product_id:
            return self._error('User-to-user chat must be started from a product page')

        shared_conv = self._find_shared_conversation(user_id, target_user_id)
        if not shared_conv:
            product_id = requested_product_id or self._default_product_id()
            if not product_id:
                return self._error('No product found to start conversation')

            shared_conv = Conversation(product_id=product_id)
            db.session.add(shared_conv)
            db.session.flush()

            db.session.add_all([
                ConversationParticipant(
                    conversation_id=shared_conv.conversation_id,
                    user_id=user_id,
                ),
                ConversationParticipant(
                    conversation_id=shared_conv.conversation_id,
                    user_id=target_user.user_id,
                ),
            ])
            db.session.commit()

        return {
            'ok': True,
            'conversation_id': shared_conv.conversation_id,
            'product_id': shared_conv.product_id,
            'target_user_id': int(target_user.user_id),
        }


chat_service = ChatService()
