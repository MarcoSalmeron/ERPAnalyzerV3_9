# routes.py
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request
from analyzer_services.app.models.schemas import AnalysisRequest
from analyzer_services.app.process.Tasks_analyzer import run_oracle_analysis
from analyzer_services.app.process.ConnectionManager import manager
import uuid
import asyncio

from schemas.schemas import ERPState
from analyzer_services.app.state import pending_responses

router = APIRouter(prefix="/impact", tags=["Impact"])

@router.post("/resume/{thread_id}")
async def resume_flow(thread_id: str, data: ERPState):
    print(f"📥 Endpoint /resume/{thread_id} llamado con: {data}")
    pending_responses[thread_id] = data.erp_module
    print(f"💾 pending_responses[{thread_id}] = {data.erp_module}")
    print(f"📋 Estado actual de pending_responses: {list(pending_responses.keys())}")
    return {"status": "ok", "thread_id": thread_id}

@router.post("/analyze")
async def start_analysis(request: AnalysisRequest, http_request: Request):

    oracle_app = http_request.app.state.oracle_graph

    thread_id = f"oracle_project_{uuid.uuid4().hex[:8]}"

    print(f"🆔 /analyze creó thread_id: {thread_id}")

    # Lanzar el proceso de los 4 agentes sin bloquear la API
    asyncio.create_task(
        run_oracle_analysis(thread_id, request.query, oracle_app,)
    )

    return {"thread_id": thread_id, "message": "Análisis en curso..."}

@router.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    await manager.connect(websocket, thread_id)
    try:
        while True:
            await websocket.receive_text() # Mantener conexión viva
    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)

