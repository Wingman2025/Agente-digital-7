import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import pathlib

app_static = FastAPI()

# Serve static files directly
BASE_DIR = pathlib.Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app_static.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Servir index.html en la raíz /
@app_static.get("/")
def read_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    return {"message": "index.html not found"}, 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080)) # Default port for static server
    uvicorn.run(app_static, host="0.0.0.0", port=port)
