import asyncio
from playwright.async_api import async_playwright
from utils import cookies_to_json


async def get_cookie_string(cookies: str, username: str, password: str):
    cookie_list = eval(cookies_to_json(cookies))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.context.add_cookies(cookie_list)

        # Navigate to the desired URL
        await page.goto('https://shopee.vn/buyer/login')

        # Fill in login credentials and submit
        await page.locator('[placeholder="Email/Số điện thoại/Tên đăng nhập"]').fill(username)
        await page.locator('[placeholder="Mật khẩu"]').fill(password)
        await page.click('button.wyhvVD')

        # Wait for some time to allow the login process to complete
        await asyncio.sleep(5)
        await page.goto('https://shopee.vn/user/account/profile')
        await asyncio.sleep(5)
        # Get updated cookies after login
        new_cookies = await page.context.cookies()

        # Format cookies into "key=value" format
        formatted_cookies = [
            f"{cookie['name']}={cookie['value']}" for cookie in new_cookies]

        # Join the formatted cookies into a single string, separating them with semicolons
        cookie_string = "; ".join(formatted_cookies)

        # Close the browser
        await browser.close()

        # Return the cookie_string
        return cookie_string