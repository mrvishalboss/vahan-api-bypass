from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import json
import asyncio

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online", "message": "API is running. Use /get_vehicle?vehicle_no=NUMBER"}

@app.get("/get_vehicle")
async def get_vehicle(vehicle_no: str = Query(..., description="Gaadi ka number")):
    async with async_playwright() as p:
        try:
            # Using a custom User-Agent helps avoid basic detection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled' # Hides the webdriver flag
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Note: Aggressive blocking removed. We need JS to run to bypass the challenge.
            
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}"
            
            # Wait for networkidle so the anti-bot JS has time to redirect to the actual JSON
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            # Give it an extra 3 seconds just in case the redirect is slow
            await page.wait_for_timeout(3000) 
            
            # Look specifically for the pre tag, as browsers often wrap raw JSON in <pre>
            try:
                content = await page.locator("pre").inner_text(timeout=5000)
            except:
                # Fallback to body if no <pre> tag is found
                content = await page.inner_text("body")
                
            await browser.close()
            
            try:
                json_data = json.loads(content)
                
                mobile_num = json_data.get("data", {}).get("mobile_no", "Not Found")
                owner_name = json_data.get("data", {}).get("vehicle_info", {}).get("data", {}).get("owner_name", "Not Found")
                
                return {
                    "status": "success", 
                    "vehicle_number": vehicle_no,
                    "owner_name": owner_name,
                    "mobile_number": mobile_num
                }
                
            except json.JSONDecodeError:
                return {
                    "status": "error", 
                    "message": "Challenge bypass nahi hua ya data valid JSON nahi hai.", 
                    "raw": content.strip() # .strip() helps clean up whitespace
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
