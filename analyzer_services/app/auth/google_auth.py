from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
import os
from datetime import datetime, timedelta
from schemas.schemas import GoogleTokenRequest
from dotenv import load_dotenv

load_dotenv(override=True)

router = APIRouter(prefix="/auth", tags=["Auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")


@router.post("/google")
async def google_login(body: GoogleTokenRequest):
    try:
        # Verifica el token con los servidores de Google
        payload = id_token.verify_oauth2_token(
            body.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

    email = payload.get("email")

        # Generar JWT propio de la aplicación
    token_data = {
        "sub": email,
        "name": payload.get("name"),
        "picture": payload.get("picture"),
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    access_token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

    return {"access_token": access_token, "email": email}