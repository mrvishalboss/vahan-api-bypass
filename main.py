from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import json
import time

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "online", 
        "message": "API is running. Use /get_vehicle?vehicle_no=NUMBER",
        "api_owner": "Vishal Boss",
        "contact": "contact on telegram @techvishalboss"
    }

@app.get("/get_vehicle")
async def get_vehicle(vehicle_no: str = Query(..., description="Gaadi ka number")):
    async with async_playwright() as p:
        try:
            # Browser setup with anti-detection args
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Cache Buster: URL के अंत में टाइमस्टैम्प
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}&_t={int(time.time())}"
            
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000) 
            
            try:
                content = await page.locator("pre").inner_text(timeout=5000)
            except:
                content = await page.inner_text("body")
                
            await browser.close()
            
            try:
                json_data = json.loads(content)
                
                mobile_num = json_data.get("mobile_number", json_data.get("mobile_no", "Not Found"))
                owner_name = json_data.get("owner_name", "Not Provided by API")
                
                return {
                    "status": "success", 
                    "vehicle_number": vehicle_no,
                    "owner_name": owner_name,
                    "mobile_number": mobile_num,
                    "api_owner": "Vishal Boss",
                    "contact": "contact on telegram @techvishalboss",
                    "debug_raw_data": json_data  # 👈 इससे असली API का डेटा दिखेगा
                }
                
            except json.JSONDecodeError:
                return {
                    "status": "error", 
                    "message": "Challenge bypass nahi hua ya data valid JSON nahi hai.", 
                    "raw": content.strip(),
                    "api_owner": "Vishal Boss",
                    "contact": "contact on telegram @techvishalboss"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e),
                "api_owner": "Vishal Boss",
                "contact": "contact on telegram @techvishalboss"
            }
