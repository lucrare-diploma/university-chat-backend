from database.database import get_connection, release_connection
from datetime import datetime

def create_message(sender_id: str, receiver_id: str, content: str):
    """
    Creează un mesaj în baza de date.
    Tabelul messages are coloanele: id, sender_id, reciever_id, content, created_at.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Database connection failed")
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO messages (id, sender_id, reciever_id, content, created_at)
            VALUES (uuid_generate_v4(), %s, %s, %s, %s)
            RETURNING id, sender_id, reciever_id, content, created_at;
        """
        now = datetime.utcnow()
        cursor.execute(query, (sender_id, receiver_id, content, now))
        message = cursor.fetchone()
        conn.commit()
        return message
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        release_connection(conn)
