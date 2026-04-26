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
            # Browser settings optimized for free server
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--single-process',
                    '--blink-settings=imagesEnabled=false'
                ]
            )
            
            # Block heavy files (Images/CSS) to save RAM
            context = await browser.new_context()
            async def block_aggressively(route):
                if route.request.resource_type in ["image", "stylesheet", "media", "font"]:
                    await route.abort()
                else:
                    await route.continue_()

            page = await context.new_page()
            await page.route("**/*", block_aggressively)
            
            # API Link
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}"
            
            # Timeout set to 60 seconds
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            content = await page.inner_text("body")
            await browser.close()
            
            try:
                json_data = json.loads(content)
                
                # Extract Mobile Number
                mobile_num = "Not Found"
                if "data" in json_data and "mobile_no" in json_data["data"]:
                    mobile_num = json_data["data"]["mobile_no"]
                
                # Final Output
                return {
                    "status": "success", 
                    "message": "Vehicle to number API available! DM to buy API @techvishalboss",
                    "vehicle_number": vehicle_no,
                    "mobile_number": mobile_num,
                    "telegram": "@techvishalboss"
                }
                
            except json.JSONDecodeError:
                return {"status": "error", "message": "Challenge bypass nahi hua ya data valid JSON nahi hai.", "raw": content}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
