from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import json

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online", "message": "API is running. Use /get_vehicle?vehicle_no=NUMBER"}

@app.get("/get_vehicle")
async def get_vehicle(vehicle_no: str = Query(..., description="Gaadi ka number")):
    async with async_playwright() as p:
        try:
            # 🔴 CRASH FIX: Docker ke liye special Chrome flags add kiye gaye hain
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage', # RAM crash rokne ke liye
                    '--disable-gpu',
                    '--single-process'
                ]
            )
            page = await browser.new_page()
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}"
            
            # 🔴 TIMEOUT FIX: networkidle ki jagah domcontentloaded aur time 60s kiya gaya hai
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            # Page ka text nikaalein
            content = await page.inner_text("body")
            await browser.close()
            
            try:
                json_data = json.loads(content)
                return {
                    "status": "success", 
                    "attribution": "Powered by Vishal Boss", 
                    "data": json_data
                }
            except json.JSONDecodeError:
                return {
                    "status": "error", 
                    "message": "Challenge bypass nahi hua ya data valid JSON nahi hai.", 
                    "raw": content
                }
                
        except Exception as e:
            # Agar koi aur error aaye toh API crash hone ke bajaye error message degi
            return {"status": "error", "message": str(e)}
