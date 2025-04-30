# Importaciones principales
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner
import os
from fastapi.staticfiles import StaticFiles
import pathlib
import asyncio
import psycopg2

# Cargar variables de entorno (.env)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear cliente OpenAI con API Key
openai_client = OpenAI(api_key=api_key)

# Definir el agente CRM
crm_agent = Agent(
    name="crm_agent",
    instructions=
    """
    Eres un agente CRM digital experto en atención al cliente y ventas. Responde de forma profesional, motivadora clara y amigable.
    Cuando el cliente saluda, automaticamente respondes felicitando y motivando al cliente por dar el primer paso hacia la automatizacion de su negocio con una frase corta.
    haces unas cuantas preguntas a los clientes sobre su tipo de negocio y cuando lo entiendas les dices que tienes algunas ideas de como se podria automatizar y mejorar la experiencia al cliente dando ideas especificas para ese cliente y su negocio.
    Explicas a los clientes en como el agente virtual puede ayudarles en su negocio para Brindar un servicio al cliente excepcional y transforma clientes potenciales en ventas.
    Explicas a los clientes como un agente puede conocer completamente tu negocio y sabe cómo se pueden ofrecer los servicios de tu negocio.
    Explicas a los clientes como el agente puede automatizar tareas repetitivas y libérarles para enfocarse en crecer.

    """,
    model="gpt-4o",
)

# Instanciar el runner con el cliente OpenAI
runner = Runner()

# Inicializar la aplicación FastAPI
app = FastAPI()

# Modelo de datos para el request (mensaje del usuario)
class ChatRequest(BaseModel):
    session_id: str
    message: str

# Modelo de datos para el historial de conversaciones
class HistoryEntry(BaseModel):
    sender: str
    message: str

# Endpoint para obtener el historial de conversaciones
from app import db

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    rows = await db.fetch_history(session_id)
    return {"messages": [{"type": r[0], "text": r[1]} for r in rows]}

# Endpoint para agregar un nuevo mensaje al historial de conversaciones
@app.post("/history/{session_id}")
async def post_history(session_id: str, entry: HistoryEntry):
    await db.insert_message(session_id, entry.sender, entry.message)
    return {"status": "ok"}

# Evento de inicio para crear la tabla de conversaciones
@app.on_event("startup")
def ensure_conversations_table():
    db.ensure_conversations_table()

# Endpoint principal para interactuar con el agente CRM
@app.post("/crm-agent")
async def crm_agent_endpoint(req: ChatRequest):
    # Guarda mensaje de usuario
    await db.insert_message(req.session_id, "user", req.message)
    # Recupera todo el historial para contexto
    rows = await db.fetch_history(req.session_id)
    # Construye el contexto concatenando los mensajes previos
    history_context = "\n".join([f"{r[0]}: {r[1]}" for r in rows])
    # Ejecuta el agente CRM usando todo el historial como input
    response = await runner.run(crm_agent, input=history_context)
    reply = response.final_output
    # Guarda respuesta del agente
    await db.insert_message(req.session_id, "agent", reply)
    return {"reply": reply}

# Endpoint de depuración para inspeccionar RunResult
@app.post("/crm-agent-debug")
async def crm_agent_debug(req: ChatRequest):
    resp = await runner.run(crm_agent, input=req.message)
    return {"attributes": dir(resp), "state": resp.__dict__}

# Ruta de verificación para saber si la API está viva
@app.get("/health")
def health():
    return {"status": "CRM Agent backend running"}

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (ideal para desarrollo)
    allow_credentials=False,  # Deshabilita credenciales para permitir origen '*'
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir frontend estático en '/'
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn, os
    port = int(os.environ.get("PORT", 8090))
    print(f"Iniciando FastAPI en el puerto {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
