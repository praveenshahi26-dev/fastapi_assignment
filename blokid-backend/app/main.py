from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, organizations

app = FastAPI(title="BlokID Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to BlokID Backend"}

# Include routers
app.include_router(auth.router)
app.include_router(organizations.router, prefix="/api")
