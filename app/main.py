# Importaciones principales
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner
import os

# Cargar variables de entorno (.env)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Crear cliente OpenAI con API Key
openai_client = OpenAI(api_key=api_key)

# Definir el agente CRM
crm_agent = Agent(
    name="crm_agent",
    instructions="Eres un agente CRM digital experto en atención al cliente y ventas. Responde de forma profesional, clara y amigable.",
    model="gpt-4o",
)

# Instanciar el runner con el cliente OpenAI
runner = Runner()

# Inicializar la aplicación FastAPI
app = FastAPI()

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (ideal para desarrollo)
    allow_credentials=False,  # Deshabilita credenciales para permitir origen '*'
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para el request (mensaje del usuario)
class ChatRequest(BaseModel):
    message: str

# Endpoint principal para interactuar con el agente CRM
@app.post("/crm-agent")
async def crm_agent_endpoint(req: ChatRequest):
    # Ejecuta el agente con el mensaje del usuario y devuelve su respuesta
    response = await runner.run(crm_agent, input=req.message)
    return {"reply": response.final_output}

# Endpoint de depuración para inspeccionar RunResult
@app.post("/crm-agent-debug")
async def crm_agent_debug(req: ChatRequest):
    resp = await runner.run(crm_agent, input=req.message)
    # Devuelve los atributos y estado interno del objeto RunResult
    return {"attributes": dir(resp), "state": resp.__dict__}

# Ruta de verificación para saber si la API está viva
@app.get("/")
def root():
    return {"status": "CRM Agent backend running"}

if __name__ == "__main__":
    import uvicorn
    print("Iniciando FastAPI en el puerto 8090...")
    uvicorn.run(app, host="127.0.0.1", port=8090)
