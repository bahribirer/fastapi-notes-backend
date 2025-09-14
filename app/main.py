from fastapi import FastAPI
from app.api import routes_auth, routes_notes
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(routes_auth.router)
app.include_router(routes_notes.router)

@app.get("/")
def health():
    return {"status": "ok"}
