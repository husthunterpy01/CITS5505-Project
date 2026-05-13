from flask import request
from flask_socketio import emit, join_room
from app.extensions import socketio
from app.service.chatservice import chat_service


@socketio.on('join_conversation')
def handle_join_conversation(conversation_payload):
    result = chat_service.join_conversation(request.sid, conversation_payload)
    if not result['ok']:
        emit('error', {'message': result['error']})
        return
    join_room(result['room'])
    emit('joined', {'conversation_id': result['conversation_id'], 'room': result['room']})


@socketio.on('load_message')
def handle_load_message(message_history_payload):
    result = chat_service.load_messages(request.sid, message_history_payload)
    if not result['ok']:
        emit('error', {'message': result['error']})
        return
    emit('message_history', {
        'conversation_id': result['conversation_id'],
        'messages': result['messages'],
    })


@socketio.on('send_message')
def handle_send_message(message_payload):
    result = chat_service.send_message(request.sid, message_payload)
    if not result['ok']:
        emit('error', {'message': result['error']})
        return
    emit('message_received', result['message'], room=result['room'])


@socketio.on('list_conversations')
def handle_list_conversations(_payload=None):
    result = chat_service.list_conversations(request.sid)
    if not result['ok']:
        emit('error', {'message': result['error']})
        return
    emit('conversations_list', {'conversations': result['conversations']})


@socketio.on('start_conversation')
def handle_start_conversation(payload):
    result = chat_service.start_conversation(request.sid, payload)
    if not result['ok']:
        emit('error', {'message': result['error']})
        return
    emit('conversation_started', {
        'conversation_id': result['conversation_id'],
        'product_id': result['product_id'],
        'target_user_id': result['target_user_id'],
    })


@socketio.on('connect')
def handle_connect(auth=None):
    _ = auth
    result = chat_service.register_connection(request.sid)
    if result.get('warning'):
        print(result['warning'])
    if result.get('user_id'):
        join_room(f"user:{result['user_id']}")
        print(f"Socket {request.sid} authenticated as user {result['user_id']}")
    else:
        print(f'Socket {request.sid} connected without authentication')
    return True


@socketio.on('mark_notification_read')
def handle_mark_notification_read(payload):
    result = chat_service.mark_notification_read(request.sid, payload)
    if not result['ok']:
        return {'ok': False, 'error': result['error']}
    return {'ok': True, 'notification_id': result.get('notification_id')}


@socketio.on('set_active_conversation')
def handle_set_active_conversation(payload):
    result = chat_service.set_active_conversation(request.sid, payload)
    if not result['ok']:
        return {'ok': False, 'error': result['error']}
    return {'ok': True, 'conversation_id': result.get('conversation_id')}


@socketio.on('disconnect')
def handle_disconnect():
    if chat_service.unregister_connection(request.sid):
        print(f'Socket {request.sid} disconnected')