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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}"
        
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=20000)
            content = await page.inner_text("body")
            await browser.close()
            
            try:
                json_data = json.loads(content)
                return {"status": "success", "attribution": "Powered by Vishal Boss", "data": json_data}
            except json.JSONDecodeError:
                return {"status": "error", "message": "Challenge bypass nahi hua.", "raw": content}
                
        except Exception as e:
            await browser.close()
            return {"status": "error", "message": str(e)}
