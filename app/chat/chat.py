from datetime import datetime
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, db
from app.models import Conversation, ConversationParticipant, Message, Product, User

# Store user info per socket ID
user_sessions = {}


@socketio.on('connect')
def handle_connect(auth=None):
    """Authenticate user on Socket.IO connection."""
    try:
        user_id = session.get('user_id')
    except Exception as exc:
        print(f'Socket connect session read failed: {exc}')
        user_id = None

    if user_id:
        user_sessions[request.sid] = {'user_id': user_id}
        print(f'Socket {request.sid} authenticated as user {user_id}')
    else:
        print(f'Socket {request.sid} connected without authentication')
    return True


@socketio.on('disconnect')
def handle_disconnect():
    """Clean up user session on disconnect."""
    if request.sid in user_sessions:
        del user_sessions[request.sid]
        print(f'Socket {request.sid} disconnected')


def get_user_id():
    """Get the authenticated user ID for the current socket."""
    # Primary: session cookie-backed Flask session per event.
    # Fallback: in-memory mapping captured on connect.
    return session.get('user_id') or user_sessions.get(request.sid, {}).get('user_id')


def _find_shared_conversation(user_id, target_user_id):
    """Return the latest conversation shared by two users, if any."""
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


def _default_product_id():
    """Provide a fallback product ID for message rows when not specified."""
    first_product = Product.query.order_by(Product.product_id.asc()).first()
    return first_product.product_id if first_product else None


@socketio.on('join_conversation')
def handle_join_conversation(conversation_payload):
    user_id = get_user_id()
    if not user_id:
        emit('error', {'message': 'User not authenticated'})
        return
    
    conversation_id = conversation_payload.get('conversation_id')
    conversation = Conversation.query.get(conversation_id)
    if not conversation:    
        emit('error', {'message': 'Conversation not found'})
        return
    related_participants = ConversationParticipant.query \
        .filter_by(conversation_id=conversation.conversation_id)\
        .all()
    
    if not any(p.user_id == user_id for p in related_participants):
        emit('error', {'message': 'User not a participant of this conversation'})
        return
    
    # join the Socket.IO room named by conversation id
    room = f"conv:{conversation.conversation_id}"
    join_room(room)
    emit('joined', {'conversation_id': conversation.conversation_id, 'room': room})
    
@socketio.on('load_message')
def handle_load_message(message_history_payload):
    user_id = get_user_id()
    if not user_id:
        emit('error', {'message': 'User not authenticated'})
        return
    
    conversation_id = message_history_payload.get('conversation_id')
    conversation = Conversation.query.get(conversation_id)
    if not conversation:    
        emit('error', {'message': 'Conversation not found'})
        return
    # return recent message history (latest 50)
    messages = Message.query.filter_by(conversation_id=conversation_id) \
        .order_by(Message.sent_at.desc())\
        .limit(50)\
        .all()
    if not messages:
        emit('message_history', {'messages': []})
        return

    message_list = [{
        'message_id': msg.message_id,
        'sender_id': msg.sender_id,
        'sender_username': f"{User.query.get(msg.sender_id).first_name} {User.query.get(msg.sender_id).last_name}",
        'content': msg.content,
        'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
        'is_read': msg.is_read,
    } for msg in reversed(messages)]

    emit('message_history', {'messages': message_list})

@socketio.on('send_message')
def handle_send_message(message_payload):
    user_id = get_user_id()
    if not user_id:
        emit('error', {'message': 'User not authenticated'})
        return
    
    conversation_id = message_payload.get('conversation_id')
    content = (message_payload.get('content') or '').strip()
    if not conversation_id or not content:
        emit('error', {'message': 'Missing conversation or message content'})
        return

    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        emit('error', {'message': 'Conversation not found'})
        return

    related_participants = ConversationParticipant.query.filter_by(conversation_id=conversation_id).all()
    if not any(p.user_id == user_id for p in related_participants):
        emit('error', {'message': 'User not a participant of this conversation'})
        return

    product_id = message_payload.get('product_id') or conversation.product_id or _default_product_id()
    if not product_id:
        emit('error', {'message': 'No product context available for this message'})
        return
    
    # Update message to be added
    message = Message(
        conversation_id=conversation_id,
        product_id=product_id,
        sender_id=user_id,
        content=content,
        sent_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    try:
        db.session.add(message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print(f'Failed to commit message for conversation {conversation_id}: {exc}')
        emit('error', {'message': 'Failed to save message. Please try again.'})
        return

    sender = User.query.get(user_id)
    # Broadcast new message to current active channel
    emit('message_received',{
        'message_id': message.message_id,
        'conversation_id': conversation_id,
        'sender_id': user_id,
        'sender_username': f"{sender.first_name} {sender.last_name}",
        'content': content,
        'sent_at': message.sent_at.isoformat()
    }, room=f"conv:{conversation_id}")


@socketio.on('list_conversations')
def handle_list_conversations(_payload=None):
    """Return all contacts with optional latest conversation metadata."""
    user_id = get_user_id()
    if not user_id:
        emit('error', {'message': 'User not authenticated'})
        return

    user = User.query.get(user_id)
    if not user:
        emit('error', {'message': 'User not found'})
        return

    out = []
    contacts = User.query.filter(User.user_id != user_id).order_by(User.first_name.asc(), User.last_name.asc()).all()
    for contact in contacts:
        shared_conv = _find_shared_conversation(user_id, contact.user_id)
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

    emit('conversations_list', {'conversations': out})


@socketio.on('start_conversation')
def handle_start_conversation(payload):
    user_id = get_user_id()
    if not user_id:
        emit('error', {'message': 'User not authenticated'})
        return

    target_user_id = payload.get('target_user_id')
    if not target_user_id:
        emit('error', {'message': 'Missing target user'})
        return
    try:
        target_user_id = int(target_user_id)
    except (TypeError, ValueError):
        emit('error', {'message': 'Invalid target user'})
        return

    if target_user_id == int(user_id):
        emit('error', {'message': 'Cannot start a conversation with yourself'})
        return

    target_user = User.query.get(target_user_id)
    if not target_user:
        emit('error', {'message': 'Target user not found'})
        return

    shared_conv = _find_shared_conversation(user_id, target_user_id)
    if not shared_conv:
        current_user = User.query.get(user_id)
        product_id = payload.get('product_id') or _default_product_id()
        if not product_id:
            emit('error', {'message': 'No product found to start conversation'})
            return

        conv_type = 'admin' if (current_user.role == 'admin' or target_user.role == 'admin') else 'direct'
        shared_conv = Conversation(product_id=product_id, conv_type=conv_type)
        db.session.add(shared_conv)
        db.session.flush()

        db.session.add_all([
            ConversationParticipant(
                conversation_id=shared_conv.conversation_id,
                user_id=user_id,
                participant_role='admin' if current_user.role == 'admin' else 'user'
            ),
            ConversationParticipant(
                conversation_id=shared_conv.conversation_id,
                user_id=target_user.user_id,
                participant_role='admin' if target_user.role == 'admin' else 'user'
            ),
        ])
        db.session.commit()

    emit('conversation_started', {
        'conversation_id': shared_conv.conversation_id,
        'product_id': shared_conv.product_id,
        'target_user_id': int(target_user.user_id),
    })