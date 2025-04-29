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
@app.get("/history/{session_id}")
async def get_history(session_id: str):
    def _fetch():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "SELECT sender, message FROM conversations WHERE session_id=%s ORDER BY ts",
            (session_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    rows = await asyncio.to_thread(_fetch)
    return {"messages": [{"type": r[0], "text": r[1]} for r in rows]}

# Endpoint para agregar un nuevo mensaje al historial de conversaciones
@app.post("/history/{session_id}")
async def post_history(session_id: str, entry: HistoryEntry):
    def _insert():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (session_id, sender, message) VALUES (%s,%s,%s)",
            (session_id, entry.sender, entry.message)
        )
        conn.commit()
        cur.close()
        conn.close()
    await asyncio.to_thread(_insert)
    return {"status": "ok"}

# Evento de inicio para crear la tabla de conversaciones
@app.on_event("startup")
def ensure_conversations_table():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            ts TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Endpoint principal para interactuar con el agente CRM
@app.post("/crm-agent")
async def crm_agent_endpoint(req: ChatRequest):
    # Guarda mensaje de usuario
    await post_history(req.session_id, HistoryEntry(sender="user", message=req.message))
    # Ejecuta el agente CRM
    response = await runner.run(crm_agent, input=req.message)
    reply = response.final_output
    # Guarda respuesta del agente
    await post_history(req.session_id, HistoryEntry(sender="agent", message=reply))
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
