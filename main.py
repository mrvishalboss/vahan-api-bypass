from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import json
import time
import base64
from playwright_stealth import stealth_async

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
            browser = await p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--window-size=1920,1080'
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            await stealth_async(page)
            
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}&_t={int(time.time())}"
            
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(6000) 
            
            try:
                await page.wait_for_selector("body", timeout=10000)
                content = await page.locator("body").inner_text()
            except:
                content = await page.content()
            
            clean_content = content.strip()
            if "{" in clean_content:
                clean_content = clean_content[clean_content.find("{"):] 
            
            try:
                json_data = json.loads(clean_content)
                await browser.close()
                
                main_data = json_data.get("data", {})
                vehicle_info_data = main_data.get("vehicle_info", {}).get("data", {})
                
                mobile_num = main_data.get("mobile_no", vehicle_info_data.get("owner_mobile", "Not Found"))
                owner_name = vehicle_info_data.get("owner_name", "Not Provided by API")
                
                return {
                    "status": "success", 
                    "vehicle_number": vehicle_no,
                    "owner_name": owner_name,
                    "mobile_number": mobile_num,
                    "api_owner": "Vishal Boss",
                    "contact": "contact on telegram @techvishalboss"
                }
                
            except json.JSONDecodeError:
                # 📸 Yahan Screenshot ka jadu hoga
                screenshot_bytes = await page.screenshot()
                base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')
                await browser.close()
                
                return {
                    "status": "error", 
                    "message": "Challenge bypass nahi hua. Check screenshot image to see what Render is seeing.", 
                    "raw_text": clean_content[:100], 
                    "screenshot_base64": base64_image, # Yahan badi si string aayegi
                    "api_owner": "Vishal Boss",
                    "contact": "contact on telegram @techvishalboss"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Browser Error: {str(e)}",
                "api_owner": "Vishal Boss",
                "contact": "contact on telegram @techvishalboss"
            }
