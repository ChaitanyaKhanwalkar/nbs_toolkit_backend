from fastapi import FastAPI
from api import water_data
from db.database import engine
from db import models
from api import location
from api import recommendations
from api import implementation
import threading
import time
import requests



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

def keep_alive():
    while True:
        try:
            requests.get("https://nbs-toolkit-backend.onrender.com/recommendations?state_name=Madhya%20Pradesh&water_type=Grey%20Water")
        except Exception as e:
            print(f"Keep-alive failed: {e}")
        time.sleep(300)  # Ping every 10 min

threading.Thread(target=keep_alive, daemon=True).start()

