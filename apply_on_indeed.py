import asyncio
import os, time, json
from playwright.async_api import async_playwright

# Function to parse JSON from a file
def parse_json_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)  # Parse JSON data
    return data

async def login_and_save_storage_state(context):
    file_path = 'env.json'  # Replace with the path to your JSON file
    parsed_data = parse_json_from_file(file_path)
    page = await context.new_page()
    await page.goto(parsed_data["URL"])

    # Perform the login process (e.g., entering username and password)
    await page.click('[data-gnav-element-name="SignIn"]')
    await page.wait_for_timeout(5000)
    await page.type('input[name="__email"]', parsed_data["EMAIL"])
    await page.wait_for_timeout(5000)
    await page.click('[data-tn-element="auth-page-email-submit-button"]')
    await page.wait_for_timeout(5000)
    await page.click('[data-tn-element="auth-page-google-password-fallback"]')
    await page.wait_for_timeout(5000)

    # enter the code from your email here, pausing the script for 60 seconds now
    print("Enter the code from your email here, pausing the script for 60 seconds now")
    time.sleep(60)

    #  After login, save the storage state
    await context.storage_state(path="storageState.json")
    print("Login successful, session saved to storageState.json")


async def main():
    async with async_playwright() as p:
        file_path = 'env.json'  # Replace with the path to your JSON file
        parsed_data = parse_json_from_file(file_path)
        browser = await p.chromium.launch(headless=False)

        # Check if storageState.json exists
        if os.path.exists("storageState.json"):
            # Reuse existing session
            print("Reusing saved session from storageState.json")
            context = await browser.new_context(storage_state="storageState.json")
        else:
            # No storageState.json, perform login and save session
            print("No saved session found. Logging in and saving session...")
            context = await browser.new_context()
            await login_and_save_storage_state(context)

        # Open a page after login (either from saved session or after logging in)
        page = await context.new_page()
        await page.goto(parsed_data["URL"])
        
        # Step 2: Perform a job search
        print("Entering job parameters now")
        await page.fill('input[name="q"]', parsed_data["WORK_TYPE"])  # Job search keyword
        await page.fill('input[name="l"]', parsed_data["COUNTRY"])  # Location keyword
        await page.press('input[name="l"]', 'Enter')
        await page.wait_for_selector('.job_seen_beacon')  # Wait until job cards are loaded

        # Rejects cookies if applicable 
        # await page.locator("[id='onetrust-reject-all-handler']").click()

        # Step 3: Loop through job listings
        job_cards = await page.query_selector_all('.job_seen_beacon h2 span')
        for i in job_cards:
            await i.click()
            print("Applying for: ", await i.text_content())
            print("Few more details:")
            time.sleep(5)
            details = await page.query_selector_all("[id='jobDescriptionText'] p")
            for detail in details:
                print(await detail.text_content())
            print("**********************************************")
            # await page.click("[id='indeedApplyButton']")


    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
