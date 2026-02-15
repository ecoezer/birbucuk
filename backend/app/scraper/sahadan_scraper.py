import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os
import sys

# Add backend directory to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from app.database import SessionLocal, init_db
from app.models.schema import Match, Odd

# Map Turkish month names to numbers if necessary, or rely on standard date formats
# sahadan might use specific formats.

URL = "https://arsiv.sahadan.com/genis_ekran_iddaa_programi/"

async def run(dates):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        init_db()
        db = SessionLocal()

        try:
            for date_str in dates:
                print(f"Processing date: {date_str}")
                await page.goto(URL, timeout=60000)
                
                # Handle Consent Popup
                try:
                    consent_button = await page.query_selector("button.fc-primary-button")
                    if consent_button:
                        await consent_button.click(timeout=5000)
                        print("Consent dismissed.")
                except:
                    pass

                # Uncheck "Sadece Oynanmamış Maçları Göster"
                checkbox = await page.query_selector("input#justNotPlayed")
                if checkbox:
                    is_checked = await checkbox.is_checked()
                    if is_checked:
                        await checkbox.click(force=True)
                        await page.wait_for_timeout(2000) # Wait for bülten to reload

                # Select date
                print(f"Selecting date: {date_str}")
                await page.evaluate(f'document.querySelector("select#dayId").value = "{date_str}"; document.querySelector("select#dayId").dispatchEvent(new Event("change"));')
                await page.wait_for_timeout(5000) # Wait for day to load

                # Wait for resultsList table to have actual match rows
                try:
                    await page.wait_for_function('document.querySelectorAll("div#dvLarge table#resultsList tr").length > 5', timeout=20000)
                except Exception as e:
                    print(f"Timeout waiting for matches: {e}")
                    await page.screenshot(path=f"error_{date_str}.png")
                    continue
                
                # Parse matches
                rows = await page.query_selector_all("div#dvLarge table#resultsList tr")
                current_league = "Unknown"
                matches_saved = 0
                
                for row in rows:
                    class_name = await row.get_attribute("class") or ""
                    
                    # Competition rows usually have class 'competition' or 'groupHeader' and a single td with colspan
                    if "competition" in class_name or "groupHeader" in class_name:
                        text = await row.inner_text()
                        if text.strip() and len(text.strip()) > 5:
                            current_league = text.strip()
                        continue
                        
                    tds = await row.query_selector_all("td")
                    if len(tds) < 10:
                        continue
                    
                    try:
                        time_text = await tds[0].inner_text()
                        home_team = await tds[5].inner_text()
                        away_team = await tds[6].inner_text()
                        iy_score = await tds[7].inner_text()
                        ms_score = await tds[8].inner_text()
                        
                        if not home_team.strip() or not away_team.strip():
                            continue

                        def parse_score(score_str):
                            if "-" in score_str:
                                try:
                                    pts = score_str.strip().split("-")
                                    return int(pts[0]), int(pts[1])
                                except:
                                    return None, None
                            return None, None

                        home_ft, away_ft = parse_score(ms_score)
                        home_ht, away_ht = parse_score(iy_score)
                        
                        dt = datetime.strptime(f"{date_str} {time_text.strip()}", "%d.%m.%Y %H:%M")
                        
                        # Use a more robust check for existing matches to avoid duplicates
                        match_obj = db.query(Match).filter(
                            Match.date == dt,
                            Match.home_team == home_team.strip(),
                            Match.away_team == away_team.strip()
                        ).first()
                        
                        if not match_obj:
                            match_obj = Match(
                                date=dt,
                                home_team=home_team.strip(),
                                away_team=away_team.strip(),
                                score_home=home_ft,
                                score_away=away_ft,
                                score_home_iy=home_ht,
                                score_away_iy=away_ht,
                                league=current_league.strip()
                            )
                            db.add(match_obj)
                            db.flush()
                        
                        odds_to_save = []
                        async def add_odd(idx, bet_type, option):
                            try:
                                val_text = await tds[idx].inner_text()
                                val = float(val_text.strip().replace(",", "."))
                                if val > 1.0:
                                    # Check if exists
                                    existing = db.query(Odd).filter(
                                        Odd.match_id == match_obj.id,
                                        Odd.bet_type == bet_type,
                                        Odd.option == option
                                    ).first()
                                    if not existing:
                                        odds_to_save.append(Odd(match_id=match_obj.id, bet_type=bet_type, option=option, odd_value=val))
                            except:
                                pass

                        # Indices based on the dvLargeHead structure observed in debug HTML:
                        # MS: 9, 10, 11
                        # IY: 12, 13, 14
                        # KG: 20, 21
                        # ÇŞ: 22, 23, 24
                        # AÜ 2.5: 29, 30
                        
                        await add_odd(9, "MS", "1")
                        await add_odd(10, "MS", "X")
                        await add_odd(11, "MS", "2")
                        
                        await add_odd(12, "IY", "1")
                        await add_odd(13, "IY", "X")
                        await add_odd(14, "IY", "2")
                        
                        await add_odd(20, "KG", "Var")
                        await add_odd(21, "KG", "Yok")
                        
                        await add_odd(22, "ÇŞ", "1-X")
                        await add_odd(23, "ÇŞ", "1-2")
                        await add_odd(24, "ÇŞ", "X-2")
                        
                        await add_odd(29, "AÜ 2.5", "Alt")
                        await add_odd(30, "AÜ 2.5", "Üst")
                        
                        if odds_to_save:
                            db.add_all(odds_to_save)
                            
                        matches_saved += 1
                        if matches_saved % 10 == 0:
                            print(f"[{date_str}] Saved {matches_saved} matches...")

                    except Exception as e:
                        db.rollback()
                        continue
                
                db.commit()
                print(f"Finished {date_str}: Total {matches_saved} matches saved.")

        finally:
            db.close()
            await browser.close()

if __name__ == "__main__":
    # Dates format: DD.MM.YYYY
    dates_to_scrape = ["13.02.2026", "14.02.2026"] 
    asyncio.run(run(dates_to_scrape))
