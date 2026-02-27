# ============================================
# FLAVOUR FLEET — Real-Time Events (Socket.IO)
# ============================================

from flask_socketio import emit, join_room

def register_socketio_events(socketio):
    """Register all Socket.IO event handlers."""

    @socketio.on('connect')
    def handle_connect():
        print('🔌 Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('🔌 Client disconnected')

    @socketio.on('track_order')
    def handle_track_order(data):
        """Client joins a room keyed by order_id for live updates."""
        order_id = data.get('order_id')
        if order_id:
            join_room(order_id)
            emit('tracking_joined', {'order_id': order_id, 'message': 'Tracking active'})
            print(f'📡 Client joined tracking room: {order_id}')


def emit_order_update(socketio, order_id, status, eta=None):
    """Emit an order status update to all clients tracking this order."""
    payload = {
        'order_id': order_id,
        'status': status,
    }
    if eta:
        payload['eta'] = eta
    socketio.emit('order_update', payload, room=order_id)
    print(f'📡 Emitted order_update for {order_id}: {status}')
