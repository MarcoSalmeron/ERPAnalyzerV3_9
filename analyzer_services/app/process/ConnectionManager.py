# analyzer_services/app/process/ConnectionManager.py
from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = []
        self.active_connections[thread_id].append(websocket)
        print(f"🔌 Conexión añadida para {thread_id}. Total: {len(self.active_connections[thread_id])}")

    def disconnect(self, websocket: WebSocket, thread_id: str):
        if thread_id in self.active_connections:
            try:
                self.active_connections[thread_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[thread_id]:
                del self.active_connections[thread_id]
            print(f"🔌 Desconectado socket para {thread_id}. Restantes: {len(self.active_connections.get(thread_id, []))}")

    async def send_update(self, thread_id: str, message: dict):
        if thread_id in self.active_connections:
            for ws in list(self.active_connections[thread_id]):
                try:
                    await ws.send_json(message)
                except Exception as e:
                    # Si falla enviar, desconectamos ese socket
                    print(f"⚠️ Error enviando a socket {thread_id}: {e}")
                    try:
                        await ws.close()
                    except:
                        pass
                    self.disconnect(ws, thread_id)
        else:
            print(f"⚠️ No hay socket conectado para: {thread_id}")

    async def close_connection(self, thread_id: str):
        if thread_id in self.active_connections:
            for ws in list(self.active_connections[thread_id]):
                try:
                    await ws.close(code=1000)
                except:
                    pass
            del self.active_connections[thread_id]
            print(f"🔌 Socket cerrado físicamente para: {thread_id}")

manager = ConnectionManager()
