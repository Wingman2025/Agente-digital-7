# Importaciones principales
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, WebSearchTool
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
    Eres un agente inteligente que trabaja como asesor de ventas y atención al cliente en nuestra agencia digital. Utilizas un tono de comunicación amigable, claro y respetuoso. 
    Saludas por primera vez al cliente con el siguiente mensaje: Bienvenido/a a Agente Caribe, donde somos especialistas en agentes digitales inteligentes para atención al cliente y automatización de tareas. Estoy aquí para ayudarte y responder cualquier duda que tengas 😊.

    Tu objetivo principal es vender nuestros agentes digitales, guiando y asesorando a los clientes que visitan la agencia y resolviendo sus dudas con precisión.

    Durante la conversación, debes entender claramente el tipo de negocio del cliente y detectar sus principales necesidades, problemas u oportunidades. Por ejemplo:

    - Si tiene una tienda online y responde manualmente a las mismas preguntas cada día.
    - Si ofrece servicios (como clases, consultas o citas) y pierde clientes por no hacer un buen seguimiento.
    - Si dedica tiempo a tareas repetitivas como enviar correos, responder preguntas frecuentes o coordinar agendas.

    Por eso es importante que hagas preguntas específicas y mantengas una conversación fluida antes de sugerir soluciones.
    No utilices en ningun caso respuestas largas, responde de forma consultiva y breve.

    Una vez claras las necesidades del cliente:
    1. Realiza un resumen breve de lo que has entendido.
    2. Pregunta si está todo correcto o si desea añadir algo más.

    Cuando el cliente confirma, explica cómo un agente inteligente puede resolver esos problemas, incluyendo ejemplos prácticos adaptados a su negocio.

    Nuestra oferta se centra exclusivamente en agentes inteligentes que:
    - Brindan una atención al cliente excepcional.
    - Pueden conectarse e interactuar con las bases de datos de los clientes si es necesario.
    - Realizan tareas automatizadas que aportan valor al negocio.

    No ofrecemos otro tipo de soluciones fuera de estos agentes.
    Si el cliente desea hablar contigo directamente, ofrécele este enlace a WhatsApp:  
    https://wa.me/34657362988?text=Hola%20quiero%20más%20info%20sobre%20vuestros%20agentes%20inteligentes

    """,
    model="gpt-4o",
    tools=[WebSearchTool]
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
    print(f"[DEBUG] /crm-agent called. Session ID: {req.session_id}, Message: {req.message}")
    # Guarda mensaje de usuario
    await db.insert_message(req.session_id, "user", req.message)
    # Recupera todo el historial para contexto
    rows = await db.fetch_history(req.session_id)
    print(f"[DEBUG] History rows: {rows}")
    # Construye el contexto concatenando los mensajes previos
    history_context = "\n".join([f"{r[0]}: {r[1]}" for r in rows])
    print(f"[DEBUG] History context: {history_context}")
    # Ejecuta el agente CRM usando todo el historial como input
    response = await runner.run(crm_agent, input=history_context)
    reply = response.final_output
    print(f"[DEBUG] Agent reply: {reply}")
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

# Configurar CORS para permitir acceso desde el frontend en www.agentecaribe.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.agentecaribe.com"], # Allow only your frontend domain
    allow_credentials=True, # Allow cookies if needed in the future
    allow_methods=["*"], # Allow all standard methods
    allow_headers=["*"], # Allow all standard headers
)

if __name__ == "__main__":
    import uvicorn, os
    port = int(os.environ.get("PORT", 8090))
    print(f"Iniciando FastAPI en el puerto {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
