from fastapi import APIRouter, HTTPException, Depends
from schemas.message import MessageCreate
from schemas.generic_response import GenericResponse
from dependencies.dependencies import get_current_user  # Funcție care extrage user-ul curent din token
from app.services.message_service import create_message

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

@router.post("/", response_model=GenericResponse)
def send_message(message: MessageCreate, current_user: dict = Depends(get_current_user)):
    """
    Trimite un mesaj de la current user către recipient.
    - **recipient_id**: ID-ul utilizatorului destinatar.
    - **content**: Conținutul mesajului.
    """
    sender_id = current_user.get("user_id")
    if not sender_id:
        raise HTTPException(status_code=401, detail="Invalid token or user data")
    try:
        # Creează mesajul în baza de date (sender_id preluat din token)
        created_message = create_message(sender_id=sender_id, receiver_id=message.recipient_id, content=message.content)
        return GenericResponse(success=True, code=200, response=created_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
