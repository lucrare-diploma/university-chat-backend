from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.database import get_connection, release_connection
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Modelul pentru cererea de creare a unui utilizator
class User(BaseModel):
    full_name: str
    email: EmailStr
    password: str

@router.post("/", response_model=dict)
def create_user(user: User):
    hashed_password = pwd_context.hash(user.password)
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        # Folosim uuid_generate_v4() pentru a genera un UUID pentru utilizator
        query = """
            INSERT INTO users (id, full_name, email, password_hash)
            VALUES (uuid_generate_v4(), %s, %s, %s)
            RETURNING id, full_name, email;
        """
        cursor.execute(query, (user.full_name, user.email, hashed_password))
        new_user = cursor.fetchone()
        conn.commit()
        return {"user": {"id": new_user[0], "full_name": new_user[1], "email": new_user[2]}}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)

# Endpoint: Obține toți utilizatorii
@router.get("/")
def get_users():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        cursor.close()
        release_connection(conn)
        return {"users": users}
    raise HTTPException(status_code=500, detail="Failed to connect to the database")

# Endpoint: Obține un utilizator după ID
@router.get("/{user_id}")
def get_user(user_id: str):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        release_connection(conn)
        if user:
            return {"user": user}
        raise HTTPException(status_code=404, detail="User not found")
    raise HTTPException(status_code=500, detail="Database connection failed")

# Endpoint: Actualizează un utilizator
@router.put("/{user_id}")
def update_user(user_id: str, user_update: dict):
    """
    Expects a JSON body with keys: 'full_name' and 'email'
    """
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            UPDATE users
            SET full_name = %s, email = %s
            WHERE id = %s
            RETURNING id, full_name, email;
        """
        cursor.execute(query, (user_update.get("full_name"), user_update.get("email"), user_id))
        updated_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        release_connection(conn)
        if updated_user:
            return {"user": updated_user}
        raise HTTPException(status_code=404, detail="User not found")
    raise HTTPException(status_code=500, detail="Database connection failed")

# Endpoint: Șterge un utilizator
@router.delete("/{user_id}")
def delete_user(user_id: str):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM users WHERE id = %s RETURNING id;"
        cursor.execute(query, (user_id,))
        deleted_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        release_connection(conn)
        if deleted_user:
            return {"message": "User deleted successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    raise HTTPException(status_code=500, detail="Database connection failed")


# # Configurăm CryptContext pentru bcrypt
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# @router.post("/hash-passwords", summary="Hash passwords for all users (temporary)")
# def hash_all_passwords():
#     """
#     Iterează peste toți utilizatorii și actualizează câmpul `password_hash` 
#     cu o valoare bcrypt hash-uită, doar dacă nu este deja hash-uită.
#     """
#     conn = get_connection()
#     if not conn:
#         raise HTTPException(status_code=500, detail="Database connection failed")
    
#     cursor = conn.cursor()
#     try:
#         # Se selectează id-ul și parola din tabelul users
#         cursor.execute("SELECT id, password_hash FROM users;")
#         users = cursor.fetchall()
#         for user in users:
#             user_id, password_value = user
#             # Presupunem că un hash bcrypt începe cu "$2b$"
#             if not password_value.startswith("$2b$"):
#                 new_hash = pwd_context.hash(password_value)
#                 cursor.execute(
#                     "UPDATE users SET password_hash = %s WHERE id = %s;",
#                     (new_hash, user_id)
#                 )
#         conn.commit()
#         return {"message": "Passwords updated successfully"}
#     except Exception as e:
#         conn.rollback()
#         raise HTTPException(status_code=500, detail=f"Error during password hashing: {e}")
#     finally:
#         cursor.close()
#         release_connection(conn)
