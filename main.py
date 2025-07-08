from fastapi import FastAPI
from api import water_data
from db.database import engine
from db import models
from api import location
from api import recommendations
from api import implementation


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
