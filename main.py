from fastapi import FastAPI
from app.api import water_data
from app.db.database import engine
from app.db import models
from app.api import location
from app.api import recommendations
from app.api import implementation


app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Register API routers
app.include_router(water_data.router)

app.include_router(location.router) 

app.include_router(recommendations.router)

app.include_router(implementation.router)

@app.get('/')
def read_root():
    return {"message": "Welcome to the NbS Toolkit API"}
