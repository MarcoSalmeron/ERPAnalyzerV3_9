from analyzer_services.app.process.ConnectionManager import manager
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.errors import GraphInterrupt
from analyzer_services.app.state import pending_responses
from tools.Tools import tool_pdf_a_base64, tool_obtener_config_bot
from analyzer_services.app.auth.auth_service import auth_service
import httpx
from common.common_utl import get_embeddings_model
import asyncio
import logging

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

##memory = MemorySaver()
##oracle_app = team.compile(checkpointer=checkpointer)
get_embeddings_model()


# --- Función de Ejecución del Grafo (Lógica Pesada) ---
async def run_oracle_analysis(thread_id: str, query: str, oracle_app):
    await asyncio.sleep(2)
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [HumanMessage(content=query)]}
    print(f"🚀 run_oracle_analysis iniciado con thread_id: {thread_id}")

    # Flag para la selección del módulo
    module_selected = False

    try:
        step_agent = 1
        await manager.send_update(thread_id, {
            "step": step_agent,
            "agent": "supervisor",
            "status": "active",
            "log": "Iniciando orquestación..."
        })

        while True:
            try:
                async for event in oracle_app.astream(inputs, config=config, stream_mode="values"):
                    if "messages" in event:
                        last_msg = event["messages"][-1]
                        if hasattr(last_msg, 'name') and last_msg.name:
                            agent_name = last_msg.name.lower()
                            logger.info(f"Detección de agente: {agent_name}")
                            steps = {"transfer_back_to_supervisor": 1, "transfer_to_investigador": 2,
                                     "transfer_to_analista": 3, "transfer_to_redactor": 4}
                            current_step = steps.get(agent_name, 1)
                            await manager.send_update(thread_id, {
                                "step": current_step,
                                "agent": agent_name,
                                "status": "active",
                                "content": last_msg.content,
                                "log": f"Ejecutando tareas de {agent_name}..."
                            })

                state = await oracle_app.aget_state(config)

                # ── Pedir módulo si no se seleccionó ──
                if not module_selected:
                    mensajes = state.values.get("messages", [])
                    pregunta = None
                    for msg in reversed(mensajes):
                        if isinstance(msg, AIMessage):
                            pregunta = msg.content
                            break
                    if pregunta is None:
                        pregunta = "Por favor selecciona el módulo ERP que deseas analizar."

                    logger.info(f"Pregunta inicial del supervisor: {pregunta}")
                    await manager.send_update(thread_id, {
                        "type": "interrupt",
                        "agent": "supervisor",
                        "content": pregunta
                    })
                    # Esperar respuesta en pending_responses...
                    while thread_id not in pending_responses:
                        await asyncio.sleep(0.5)
                    respuesta = pending_responses.pop(thread_id)
                    print(f"📤 Recuperado de pending_responses[{thread_id}]: {respuesta}")

                    await oracle_app.aupdate_state(config, {"erp_module": respuesta})
                    inputs = {"messages": [HumanMessage(content=respuesta)]}
                    module_selected = True

                    continue

                # ── Verificar si terminó ─────
                if not state.next:
                    # ── 1. Enviar el PDF al frontend ──────────────────────────
                    filename = f"reporte_{thread_id}.pdf"
                    await manager.send_update(thread_id, {
                        "step": 4,
                        "agent": "redactor",
                        "status": "completed",
                        "pdf_ready": True,
                        "pdf_url": f"/static/reports/{filename}"
                    })

                    # ── 2. Interrupt: preguntar sobre pruebas de regresión ────
                    await manager.send_update(thread_id, {
                        "type": "interrupt",
                        "agent": "system",
                        "content": "¿Deseas generar un plan de pruebas de regresión para los impactos detectados? (Sí / No)"
                    })

                    # ── 3. Esperar respuesta del usuario ──────────────────────
                    while thread_id not in pending_responses:
                        await asyncio.sleep(0.5)
                    respuesta_regresion = pending_responses.pop(thread_id)
                    logger.info(f"📋 Respuesta pruebas de regresión: {respuesta_regresion}")

                    # ── 4. Procesar respuesta y notificar al frontend ─────────
                    if respuesta_regresion.strip().lower() in ("sí", "si", "s", "yes", "y"):

                        try:
                            # 1. PDF en base64
                            pdf_data = tool_pdf_a_base64.invoke({"thread_id": thread_id})

                            # 2. Obtener config del bot
                            nombre_bot = pending_responses.get(f"{thread_id}_bot", "Envio de correo Marco")
                            config_bot = tool_obtener_config_bot.invoke({"nombre_bot" : nombre_bot})

                            # 3. body
                            body = {
                                "bot_name": config_bot["nombre_bot"],
                                "execute_bot": config_bot["execute_bot"],
                                "agent_name": config_bot["nombre_agente"],
                                "execution_variables": {
                                    "vPdfBase64": pdf_data
                                }
                            }

                            # 4. Obtener token JWT y hacer POST
                            token = await auth_service.get_token()
                            endpoint = config_bot["endpoint"]

                            async with httpx.AsyncClient() as client:
                                resp = await client.post(
                                    endpoint,
                                    json=body,
                                    headers={
                                        "Content-Type": "application/json",
                                        "Authorization": f"Bearer {token}"
                                    }
                                )

                            if resp.status_code == 200:
                                await manager.send_update(thread_id, {
                                    "type": "info",
                                    "agent": "system",
                                    "content": f"Pruebas de regresión iniciadas correctamente en {config_bot['nombre_bot']}."
                                })
                            else:
                                await manager.send_update(thread_id, {
                                    "type": "info",
                                    "agent": "system",
                                    "content": f"Error al iniciar pruebas: {resp.status_code} - {resp.text}"
                                })
                        except Exception as e:
                            logger.error(f"Error ejecutando pruebas de regresión: {e}")
                            await manager.send_update(thread_id, {
                                "type": "info",
                                "agent": "system",
                                "content": f"Error técnico al ejecutar pruebas: {str(e)}"
                            })
                    else:
                        await manager.send_update(thread_id, {
                            "type": "info",
                            "agent": "system",
                            "content": "De acuerdo. El reporte está listo para su revisión."
                        })

                        # ── 5. Cerrar conexión ────────────────────────────────────
                    await manager.close_connection(thread_id)
                    break

                continue

            except GraphInterrupt as gi:
                # Manejo de interrupciones provenientes del grafo
                try:
                    pregunta = gi.args[0].value
                except Exception:
                    pregunta = str(gi)
                logger.info(f"🤖 Interrupción capturada: {pregunta}")
                await manager.send_update(thread_id, {
                    "type": "interrupt",
                    "agent": "system",
                    "content": pregunta
                })
                while thread_id not in pending_responses:
                    await asyncio.sleep(0.5)
                respuesta = pending_responses.pop(thread_id)
                print(f"📤 Recuperado de pending_responses[{thread_id}]: {respuesta}")
                await oracle_app.aupdate_state(config, {"erp_module": respuesta})
                new_state = await oracle_app.aget_state(config)
                logger.info(f"📊 Estado actualizado: {new_state.values}")
                inputs = {"messages": [HumanMessage(content=respuesta)]}
                # Si la interrupción provino del sistema y aún no se había seleccionado módulo, marcarlo
                if not module_selected:
                    module_selected = True
                # Volver a procesar astream con la nueva entrada
                continue

    except Exception as e:
        logger.error(f"Error en el flujo de trabajo: {str(e)}")
        await manager.send_update(thread_id, {"error": str(e)})
