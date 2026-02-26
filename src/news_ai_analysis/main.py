# Точка входа в приложение fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI-анализ новостей",
    version="1.0.0",
    root_path="/api"
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)
