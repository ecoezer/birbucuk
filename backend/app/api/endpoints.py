from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import SessionLocal
from app.models.schema import Match, Odd
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class OddSchema(BaseModel):
    id: int
    bet_type: str
    option: str
    odd_value: float
    is_winning: bool
    class Config:
        orm_mode = True

class MatchSchema(BaseModel):
    id: int
    date: datetime
    home_team: str
    away_team: str
    score_home: Optional[int]
    score_away: Optional[int]
    score_home_iy: Optional[int]
    score_away_iy: Optional[int]
    league: Optional[str]
    odds: List[OddSchema] = []
    class Config:
        orm_mode = True

@router.get("/matches", response_model=List[MatchSchema])
def get_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches = db.query(Match).offset(skip).limit(limit).all()
    return matches

@router.get("/matches/{match_id}", response_model=MatchSchema)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.get("/stats/correlations")
def get_correlations(db: Session = Depends(get_db)):
    # Simple correlation analysis: how many times each odd value range wins
    # This is a placeholder for more advanced Pandas analysis later
    winning_odds = db.query(Odd).filter(Odd.is_winning == True).all()
    results = {}
    for o in winning_odds:
        key = f"{o.bet_type} - {o.option}"
        if key not in results:
            results[key] = []
        results[key].append(o.odd_value)
    
    analysis = {}
    for key, values in results.items():
        analysis[key] = {
            "count": len(values),
            "avg_winning_odd": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0
        }
    
    return analysis
