from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import auth_router, medication_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medico+ API")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your deployed frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(medication_router) 