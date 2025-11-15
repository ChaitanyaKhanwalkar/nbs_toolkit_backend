from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.responses import StatesResponse
from app.db.models import District

router = APIRouter()

@router.get("/states", response_model=StatesResponse)
def get_all_states(db: Session = Depends(get_db)):
    """
    Returns a sorted list of all unique states from district_data.
    """
    states = db.query(District.state_name).distinct().order_by(District.state_name).all()
    state_list = [state[0] for state in states]
    return StatesResponse(states=state_list)
