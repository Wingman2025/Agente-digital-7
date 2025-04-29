# Agente Caribe CRM - Backend & Frontend

Este proyecto implementa un agente CRM digital para el home page, usando FastAPI + OpenAI Agents en el backend y un widget de chat modular en el frontend.

## Estructura
- **Frontend:** HTML, CSS y JS modular (`chat-widget.js`)
- **Backend:** Python + FastAPI + OpenAI Agents (`agents==0.0.13`, `openai==1.70.0`)
- **DB:** PostgreSQL (a integrar)

## Desarrollo local
1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el backend:
   ```bash
   uvicorn main:app --reload --port 8080
   ```
3. Abre el `index.html` en tu navegador o sirve el frontend con un servidor estático.

## Endpoints principales
- `POST /crm-agent` — Recibe mensajes del chat y responde (pronto con IA real)

## Despliegue
- Railway recomendado:
  1. Conecta tu repositorio a Railway.
  2. En Settings > Environment Variables, añade:
     - OPENAI_API_KEY: tu clave de OpenAI
     - DATABASE_URL: tu cadena de conexión a PostgreSQL
  3. Railway detectará `nixpacks.toml` y ejecutará automaticamente el build/start.

## Notas
- Integraremos pronto la conexión OpenAI Agents y PostgreSQL.
- El frontend está listo para consumir el backend vía fetch/AJAX.
