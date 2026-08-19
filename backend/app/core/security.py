from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_security(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For local desktop/web app, enable localhost origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
