import json
import os
import time
from playwright.sync_api import sync_playwright

def save_json_data(data, filename):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def scrape_tval_now():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)  # Set headless=True for headless mode
        page = browser.new_page()

        # Track the number of ongoing requests
        ongoing_requests = 0

        # Intercept network requests
        def handle_request(route, request):
            nonlocal ongoing_requests
            ongoing_requests += 1
            try:
                if "init-SAAS_KANTO.json" in request.url:
                    response = route.fetch()
                    json_data = response.json()
                    save_json_data(json_data, 'TVRatings/init-SAAS_KANTO.json')
                    print("JSON data saved to TVRatings/init-SAAS_KANTO.json")
                elif "init-SAAS_KANSAI.json" in request.url:
                    response = route.fetch()
                    json_data = response.json()
                    save_json_data(json_data, 'TVRatings/init-SAAS_KANSAI.json')
                    print("JSON data saved to TVRatings/init-SAAS_KANSAI.json")
                elif "init-SAAS_CHUKYO.json" in request.url:
                    response = route.fetch()
                    json_data = response.json()
                    save_json_data(json_data, 'TVRatings/init-SAAS_CHUKYO.json')
                    print("JSON data saved to TVRatings/init-SAAS_CHUKYO.json")
            except Exception as e:
                print(f"Error handling request: {e}")
            finally:
                ongoing_requests -= 1
                route.continue_()

        page.route("**/*", handle_request)

        # Navigate to the website
        page.goto("https://tval-now.switch-m.com/", wait_until='load')
        time.sleep(5)  # Wait for the page to fully load

        # Click on the "関西" tab to load the "init-SAAS_KANSAI.json" data
        page.click('div#headlessui-radiogroup-option-4')
        time.sleep(5)  # Wait for the network request to complete

        # Click on the "中京" tab to load the "init-SAAS_CHUKYO.json" data
        page.click('div#headlessui-radiogroup-option-6')
        time.sleep(5)  # Wait for the network request to complete

        # Wait for all ongoing requests to complete
        while ongoing_requests > 0:
            time.sleep(1)

        # Close the browser
        browser.close()

if __name__ == "__main__":
    scrape_tval_now()
