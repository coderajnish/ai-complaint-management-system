from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models.complaint_model import Complaint
from routes.complaint_routes import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIVOA Complaint AI System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include complaint routes
app.include_router(router, prefix="/complaints", tags=["Complaints"])

@app.get("/")
def root():
    return {"message": "AIVOA AI Complaint System Running"}