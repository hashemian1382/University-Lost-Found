from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, database

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Setup CORS (To allow Frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Lost & Found API"}

# Example Endpoint: Get all items
@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()