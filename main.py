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
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--single-process'
                ]
            )
            page = await browser.new_page()
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}"
            
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            content = await page.inner_text("body")
            await browser.close()
            
            try:
                json_data = json.loads(content)
                
                # Mobile Number निकालने का लॉजिक
                mobile_num = "Not Found"
                if "data" in json_data and "mobile_no" in json_data["data"]:
                    mobile_num = json_data["data"]["mobile_no"]
                
                # 🔴 बिल्कुल आपके माँगे हुए फॉर्मेट में नया रिस्पॉन्स
                return {
                    "status": "success", 
                    "vehicle_number": vehicle_no,
                    "mobile_number": mobile_num,
                    "telegram": "@techvishalboss"
                }
                
            except json.JSONDecodeError:
                return {
                    "status": "error", 
                    "message": "Challenge bypass nahi hua ya data valid JSON nahi hai.", 
                    "raw": content
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
