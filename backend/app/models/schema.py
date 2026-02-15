from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base, engine, SessionLocal

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    home_team = Column(String)
    away_team = Column(String)
    score_home = Column(Integer, nullable=True)
    score_away = Column(Integer, nullable=True)
    score_home_iy = Column(Integer, nullable=True)
    score_away_iy = Column(Integer, nullable=True)
    league = Column(String, nullable=True)
    
    odds = relationship("Odd", back_populates="match")

    def __repr__(self):
        return f"<Match(date='{self.date}', home='{self.home_team}', away='{self.away_team}', score='{self.score_home}-{self.score_away}')>"

class Odd(Base):
    __tablename__ = 'odds'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    bet_type = Column(String) # e.g., 'MS', 'KG', '2.5 Alt/Ust'
    option = Column(String)   # e.g., '1', '0', '2', 'Var', 'Yok', 'Alt', 'Ust'
    odd_value = Column(Float)
    is_winning = Column(Boolean, default=False)

    match = relationship("Match", back_populates="odds")

    def __repr__(self):
        return f"<Odd(type='{self.bet_type}', option='{self.option}', value={self.odd_value}, win={self.is_winning})>"

if __name__ == "__main__":
    from app.database import init_db
    init_db()
    print("Database initialized.")
