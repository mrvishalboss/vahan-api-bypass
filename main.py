from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import json
import time
from playwright_stealth import stealth_async # Stealth Bypass Library

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
            # WAF bypass ke liye Pro Browser Setup
            browser = await p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--window-size=1920,1080' # Asli screen size dikhana zaruri hai
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            
            # 🔴 STEALTH MODE ACTIVATE - Ye InfinityFree/Cloudflare ko bypass karega
            await stealth_async(page)
            
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}&_t={int(time.time())}"
            
            # networkidle free hosting par atak jata hai, domcontentloaded safe hai
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            # ⏳ सिक्योरिटी चैलेंज (JS Check) को पास होने के लिए थोड़ा एक्स्ट्रा टाइम 
            await page.wait_for_timeout(6000) 
            
            try:
                await page.wait_for_selector("body", timeout=10000)
                content = await page.locator("body").inner_text()
            except:
                content = await page.content()
                
            await browser.close()
            
            # Data Cleanup (Free hosting ke extra HTML tags hatane ke liye)
            clean_content = content.strip()
            if "{" in clean_content:
                # Sirf { se shuru hone wala actual JSON extract karega
                clean_content = clean_content[clean_content.find("{"):] 
            
            # JSON पार्सिंग
            try:
                json_data = json.loads(clean_content)
                
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
                # Agar fail hua toh logs ko clean rakhne ke liye sirf shuru ka WAF page code dikhayega
                return {
                    "status": "error", 
                    "message": "Challenge bypass nahi hua ya data valid JSON nahi hai.", 
                    "raw": clean_content[:300], 
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
