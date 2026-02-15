from app.database import SessionLocal
from app.models.schema import Match, Odd

def process_data():
    db = SessionLocal()
    try:
        matches = db.query(Match).all()
        print(f"Processing {len(matches)} matches...")
        
        for match in matches:
            # 1. Clean league name (remove date patterns if present)
            if match.league and (match.league.endswith(".2026") or "Paz" in match.league or "Cmt" in match.league):
                # This was likely a date header, we should probably look for the previous non-date header
                # but for now let's just mark it for manual fix or skip logic
                pass
            
            if match.score_home is None or match.score_away is None:
                continue
                
            sh = match.score_home
            sa = match.score_away
            sh_iy = match.score_home_iy
            sa_iy = match.score_away_iy
            total = sh + sa
            
            # 2. Calculate winning odds
            odds = db.query(Odd).filter(Odd.match_id == match.id).all()
            for odd in odds:
                is_win = False
                if odd.bet_type == "MS":
                    if odd.option == "1" and sh > sa: is_win = True
                    elif odd.option == "X" and sh == sa: is_win = True
                    elif odd.option == "2" and sh < sa: is_win = True
                elif odd.bet_type == "IY":
                    if sh_iy is not None and sa_iy is not None:
                        if odd.option == "1" and sh_iy > sa_iy: is_win = True
                        elif odd.option == "X" and sh_iy == sa_iy: is_win = True
                        elif odd.option == "2" and sh_iy < sa_iy: is_win = True
                elif odd.bet_type == "KG":
                    if odd.option == "Var" and sh > 0 and sa > 0: is_win = True
                    elif odd.option == "Yok" and (sh == 0 or sa == 0): is_win = True
                elif odd.bet_type == "AÜ 2.5":
                    if odd.option == "Alt" and total < 2.5: is_win = True
                    elif odd.option == "Üst" and total > 2.5: is_win = True
                elif odd.bet_type == "ÇŞ":
                    if odd.option == "1-X" and sh >= sa: is_win = True
                    elif odd.option == "1-2" and sh != sa: is_win = True
                    elif odd.option == "X-2" and sh <= sa: is_win = True
                
                odd.is_winning = is_win
            
        db.commit()
        print("Data processing complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    process_data()
