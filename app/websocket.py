from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import ConnectionManager
from app.utils.auth import verify_token
from app.models.user import User

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/messages")
async def websocket_messages(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    user = await User.find_one(User.username == payload.get("username"))
    if not user:
        await websocket.close(code=1008)
        return

    user_id = str(user.id)
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
