from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as user_router  # or whatever your import is
from gemini_chat import gemini_router

app = FastAPI()

# ✅ Enable CORS for React frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],  # include "OPTIONS"
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(gemini_router)