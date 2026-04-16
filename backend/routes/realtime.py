# ============================================
# FLAVOUR FLEET — Real-Time Events (Socket.IO)
# ============================================

from flask_socketio import emit, join_room

from helpers import logger


def register_socketio_events(socketio):
    """Register all Socket.IO event handlers."""

    @socketio.on("connect")
    def handle_connect(auth=None):
        logger.info("Socket client connected")

    @socketio.on("disconnect")
    def handle_disconnect(reason=None):
        logger.info("Socket client disconnected")

    @socketio.on("track_order")
    def handle_track_order(data):
        """Client joins a room keyed by order_id for live updates."""
        order_id = (data or {}).get("order_id")
        if order_id:
            join_room(order_id)
            emit(
                "tracking_joined", {"order_id": order_id, "message": "Tracking active"}
            )
            logger.info("Client joined tracking room: %s", order_id)


def emit_order_update(socketio, order_id, status, eta=None):
    """Emit an order status update to all clients tracking this order."""
    room = str(order_id).strip() if order_id is not None else ""
    if not room:
        logger.warning("Skipped socket emit due to missing order_id")
        return

    payload = {
        "order_id": room,
        "status": status,
    }
    if eta:
        payload["eta"] = eta
    try:
        socketio.emit("order_update", payload, room=room, namespace="/")
        logger.info("Emitted order update for %s: %s", room, status)
    except Exception as e:
        logger.error("Socket emit failed for %s: %s", room, e, exc_info=True)
