from flask import Flask, render_template, request, jsonify
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def simulate_human_behavior(driver):
    try:
        window_size = driver.get_window_size()
        x_offset = random.randint(0, window_size['width'] - 1)
        y_offset = random.randint(0, window_size['height'] - 1)
        ActionChains(driver).move_by_offset(x_offset, y_offset).perform()
        time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"Error simulating human behavior: {e}")

def open_youtube_with_proxy(video_data):
    # NordVPN Proxy Configuration
    # proxy_address = "194.35.123.92"
    # proxy_http_port = "80"
    # proxy_ssl_port = "443"

    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--window-size=800,600")
    
    # Proxy Configuration
    # chrome_options.add_argument(f"--proxy-server=http://{proxy_address}:{proxy_http_port}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.youtube.com")
        print("Opened YouTube with NordVPN proxy!")

        try:
            consent_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Reject all') or contains(text(),'Accept all')]"))
            )
            consent_button.click()
            print("Consent form handled successfully.")
        except Exception:
            print("Consent form not found or already handled.")

        video_list = []
        for video in video_data:
            video_list.extend([video['url']] * video['views'])

        random.shuffle(video_list)

        for video_url in video_list:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            simulate_human_behavior(driver)
            driver.get(video_url)

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "video")))
                driver.execute_script("document.querySelector('video').muted = true;")
            except Exception as e:
                print(f"Error finding video element: {e}")

            watch_time = random.randint(30, 45)
            print(f"Watching video for {watch_time} seconds...")
            time.sleep(watch_time)

            simulate_human_behavior(driver)

            pause_time = random.randint(5, 10)
            print(f"Pausing for {pause_time} seconds before the next video...")
            time.sleep(pause_time)

        time.sleep(5)
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redirect', methods=['POST'])
def redirect_videos():
    video_data = request.json

    if not isinstance(video_data, list):
        return jsonify({'success': False, 'message': 'Invalid data format'})

    try:
        open_youtube_with_proxy(video_data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
