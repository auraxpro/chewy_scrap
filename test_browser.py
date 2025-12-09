"""Test script to check if browser can launch"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        print("Launching browser...")
        # Try Firefox instead
        browser = await p.firefox.launch(headless=False)
        print("Browser launched!")
        await asyncio.sleep(2)
        print(f"Browser connected: {browser.is_connected()}")
        
        print("Creating context...")
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        print("Context created!")
        await asyncio.sleep(1)
        print(f"Browser still connected: {browser.is_connected()}")
        
        print("Creating page...")
        page = await context.new_page()
        print("Page created!")
        
        print("Navigating to Google...")
        await page.goto("https://www.google.com", wait_until="domcontentloaded")
        print("Success!")
        
        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())

