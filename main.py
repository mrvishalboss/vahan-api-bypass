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
            # Playwright ब्राउज़र सेटअप (Anti-bot बाईपास के लिए)
            # अगर फिर भी खाली डेटा आए, तो टेस्टिंग के लिए headless=False करके देखें
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
            
            # Cache Buster के साथ टारगेट URL
            target_url = f"https://api-by-black-hats-hackers.kesug.com/vehicle-api.php?vehicle_no={vehicle_no}&_t={int(time.time())}"
            
            # पेज लोड होने का इंतज़ार
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            # ⏳ सिक्योरिटी चैलेंज (JS Check) को पास होने के लिए 5 सेकंड का समय दिया है
            await page.wait_for_timeout(5000) 
            
            # डेटा एक्सट्रेक्ट करना (सुनिश्चित करना कि body लोड हो चुकी है)
            try:
                await page.wait_for_selector("body", timeout=10000)
                # पहले <pre> टैग ढूंढने की कोशिश करेगा (जहाँ आमतौर पर JSON होता है)
                content = await page.locator("pre").inner_text(timeout=5000)
            except:
                # अगर <pre> नहीं मिला, तो पूरा <body> रीड करेगा
                content = await page.inner_text("body")
                
            await browser.close()
            
            # JSON पार्सिंग और डेटा फ़िल्टरिंग
            try:
                json_data = json.loads(content)
                
                # मुख्य डेटा ब्लॉक को टार्गेट करना
                main_data = json_data.get("data", {})
                vehicle_info_data = main_data.get("vehicle_info", {}).get("data", {})
                
                # मोबाइल नंबर और ओनर का नाम निकालना
                mobile_num = main_data.get("mobile_no", vehicle_info_data.get("owner_mobile", "Not Found"))
                owner_name = vehicle_info_data.get("owner_name", "Not Provided by API")
                
                # फाइनल रिस्पॉन्स रिटर्न करना
                return {
                    "status": "success", 
                    "vehicle_number": vehicle_no,
                    "owner_name": owner_name,
                    "mobile_number": mobile_num,
                    "api_owner": "Vishal Boss",
                    "contact": "contact on telegram @techvishalboss"
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
