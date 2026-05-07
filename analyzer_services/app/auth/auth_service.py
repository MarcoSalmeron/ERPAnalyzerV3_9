import httpx
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
from common.common_utl import get_conn
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.login_url = "https://boot-app.i-condor.com/api/auth/login"
        self.access_token: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        # Clave de desencriptación desde variable de entorno
        secret_key = os.environ.get("AUTH_SECRET_KEY")
        if not secret_key:
            raise RuntimeError("Variable de entorno AUTH_SECRET_KEY no definida")
        self._fernet = Fernet(secret_key.encode())

    def _get_credentials(self) -> dict:
        """Lee y desencripta credenciales desde config_auth en pgvector"""
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT username, password_enc FROM config_auth "
                "WHERE service = 'i-condor' AND active = true LIMIT 1"
            )
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                username = row[0]
                password = self._fernet.decrypt(row[1].encode()).decode()
                return {"username": username, "password": password}
        except Exception as e:
            logger.error(f"Error leyendo credenciales: {e}")
        raise RuntimeError("No se pudieron obtener credenciales desde config_auth")

    async def login(self) -> bool:
        async with self._lock:
            try:
                creds = self._get_credentials()
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        self.login_url,
                        json=creds,
                        headers={"Content-Type": "application/json"}
                    )
                    if resp.status_code == 200:
                        self.access_token = resp.json()["access_token"]
                        self.expires_at = datetime.now() + timedelta(minutes=9)
                        logger.info("Token JWT renovado exitosamente")
                        return True
                    logger.error(f"Login fallido: {resp.status_code} - {resp.text}")
            except Exception as e:
                logger.error(f"Error en login: {e}")
            return False

    async def get_token(self) -> Optional[str]:
        """Retorna token válido, hace login automático si expiró"""
        if not self.access_token or datetime.now() >= self.expires_at:
            await self.login()
        return self.access_token


auth_service = AuthService()