from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

app = FastAPI(title="轰界法术生成器", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://154.219.106.185",
        "https://hongworld.online",
        "http://hongworld.online",
    ],
    allow_origin_regex=r"^http://(127\.0\.0\.1|localhost):517\d$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "轰界法术生成器", "status": "ready"}
