from fastapi import APIRouter, HTTPException
from database.database import get_connection, release_connection
from schemas.user import UserCreate, UserResponse
from schemas.generic_response import GenericResponse
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",  # Rutele vor fi accesibile la /user, conform preferinței
    tags=["user"]
)

# Configurare pentru hashing cu bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=GenericResponse)
def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO users (id, full_name, email, password_hash)
            VALUES (uuid_generate_v4(), %s, %s, %s)
            RETURNING id, full_name, email, password_hash;
        """
        cursor.execute(query, (user.full_name, user.email, hashed_password))
        new_user = cursor.fetchone()
        conn.commit()
        created_user = UserResponse(
            id=new_user[0],
            full_name=new_user[1],
            email=new_user[2],
            password_hash=new_user[3]
        )
        return GenericResponse(success=True, code=200, response=created_user)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)

@router.get("/", response_model=GenericResponse)
def get_users():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, full_name, email, password_hash FROM users;")
        rows = cursor.fetchall()
        users = [
            UserResponse(
                id=row[0],
                full_name=row[1],
                email=row[2],
                password_hash=row[3]
            )
            for row in rows
        ]
        return GenericResponse(success=True, code=200, response=users)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)

@router.get("/{user_id}", response_model=GenericResponse)
def get_user(user_id: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, full_name, email, password_hash FROM users WHERE id = %s;", (user_id,))
        row = cursor.fetchone()
        if row:
            user = UserResponse(
                id=row[0],
                full_name=row[1],
                email=row[2],
                password_hash=row[3]
            )
            return GenericResponse(success=True, code=200, response=user)
        return GenericResponse(success=False, code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)

@router.put("/{user_id}", response_model=GenericResponse)
def update_user(user_id: str, user_update: UserCreate):
    """
    Actualizează numele și email-ul unui utilizator.
    Parola nu se actualizează aici.
    """
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    try:
        query = """
            UPDATE users
            SET full_name = %s, email = %s
            WHERE id = %s
            RETURNING id, full_name, email, password_hash;
        """
        cursor.execute(query, (user_update.full_name, user_update.email, user_id))
        row = cursor.fetchone()
        conn.commit()
        if row:
            updated_user = UserResponse(
                id=row[0],
                full_name=row[1],
                email=row[2],
                password_hash=row[3]
            )
            return GenericResponse(success=True, code=200, response=updated_user)
        return GenericResponse(success=False, code=404, detail="User not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)

@router.delete("/{user_id}", response_model=GenericResponse)
def delete_user(user_id: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    try:
        query = "DELETE FROM users WHERE id = %s RETURNING id;"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        conn.commit()
        if row:
            return GenericResponse(success=True, code=200, response={"id": row[0]}, detail="User deleted successfully")
        return GenericResponse(success=False, code=404, detail="User not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)
