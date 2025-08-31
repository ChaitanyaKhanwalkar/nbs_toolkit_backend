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
from db.database import engine, wait_for_db, SessionLocal
from db import models
from api import recommendations, water_data, implementation 



app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Register API routers
app.include_router(water_data.router)

app.include_router(location.router) 

app.include_router(recommendations.router)

app.include_router(implementation.router)


def _keep_alive():
    while True:
        try:
            # hit a "real" endpoint to keep dyno + DB warm
            requests.get(
                "https://nbs-toolkit-backend.onrender.com/recommendations?state_name=Madhya%20Pradesh&water_type=Grey%20Water",
                timeout=10,
            )
            print("✅ keep-alive ping sent")
        except Exception as e:
            print(f"⚠️ keep-alive failed: {e}")
        time.sleep(600)  # 10 min

@app.on_event("startup")
def on_startup():
    # 1) wait for DB (handles DNS / cold start)
    wait_for_db()
    # 2) only now touch metadata
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        # don't crash the app; logs will show error, endpoints can still run if they don't need schema ops
        print(f"⚠️ create_all failed: {e}")

    # 3) start keep-alive thread (non-blocking)
    t = threading.Thread(target=_keep_alive, daemon=True)
    t.start()

@app.get("/healthz")
def healthz():
    # simple liveness; optional: try a lightweight DB ping here
    return {"status": "ok"}

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

