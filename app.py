from flask import Flask, render_template, request, jsonify
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def open_youtube_incognito(video_data):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--mute-audio")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for video in video_data:
            url = video['url']
            views = video['views']

            for _ in range(views):
                driver.execute_script("window.open('');")
                windows = driver.window_handles
                driver.switch_to.window(windows[-1])
                driver.get(f"{url}?autoplay=1")

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "video"))
                    )

                    driver.execute_script("""
                        var video = document.querySelector('video');
                        if (video) {
                            console.log('Muting video...');
                            video.muted = true;
                        } else {
                            console.log('Video element not found.');
                        }
                    """)
                except Exception as e:
                    print(f"Error waiting for video element: {e}")

                time.sleep(10)

        time.sleep(5)
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redirect', methods=['POST'])
def redirect():
    video_data = request.json

    if not isinstance(video_data, list):
        return jsonify({'success': False, 'message': 'Invalid data format'})

    try:
        open_youtube_incognito(video_data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=5000)
