import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.message_service import create_message
from typing import Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Dicționar: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

# Instanța managerului de conexiuni
manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    Fiecare client se conectează la /ws/{user_id}. 
    Mesajele sunt trimise în format JSON, de exemplu:
    {
      "recipient_id": "dest_user_id",
      "content": "Hello!"
    }
    IMPORTANT: sender_id este întotdeauna preluat din URL (user_id) și nu poate fi specificat de client.
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text("Invalid message format. Expected JSON.")
                continue

            recipient_id = message_data.get("recipient_id")
            content = message_data.get("content")
            if not recipient_id or not content:
                await websocket.send_text("Missing recipient_id or content.")
                continue

            # Folosește user_id din URL ca sender_id, asigurând că clientul nu poate modifica acest lucru
            try:
                message = create_message(sender_id=user_id, receiver_id=recipient_id, content=content)
            except Exception as e:
                await websocket.send_text(f"Failed to create message: {e}")
                continue

            # Confirmare către expeditor
            await websocket.send_text("Message sent successfully.")
            # Trimite mesajul și către destinatar, dacă este conectat
            await manager.send_personal_message(data, recipient_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
