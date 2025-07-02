from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, organizations, websites
from app.database import engine
from app.models import user, organization, website

user.Base.metadata.create_all(bind=engine)
organization.Base.metadata.create_all(bind=engine)
website.Base.metadata.create_all(bind=engine)

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
app.include_router(websites.router)

@app.get("/")
def root():
    return {"message": "Organization Website Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
