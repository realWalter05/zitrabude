from instagrapi import Client
from pathlib import Path
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from PIL import Image, ImageOps
import requests
from datetime import timedelta, datetime, date
from io import BytesIO
import os
import random
import time
import cv2


def get_pocasi():
    # Sets up selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)      
    
    # Get image in browser
    url = "https://ct24.ceskatelevize.cz/pocasi/zitra"
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 250);")
    driver.get_screenshot_as_file("pocasi.png")
    
    print("Pocasi saved")
    return Image.open("pocasi.png")


def crop_screen_img(screen):
    cropped_image = screen.crop((566, 163, 1340, 647))

    # Saving the image
    rgb_image = cropped_image.convert('RGB')
    return rgb_image


def crop_to_template(image):
    # Convert to grayscale
    mask = Image.open('./img/map_mask.jpg').convert('L')

    # Threshold and invert the colors (white will be transparent)
    mask = mask.point(lambda x: x < 100 and 255)

    # The size of the images must match before apply the mask
    img = ImageOps.fit(image, mask.size)

    img.putalpha(mask) # Modifies the original image without return    
    return img


def change_opacity(img):
    A = img.getchannel('A')
    # Make all opaque pixels into semi-opaque
    newA = A.point(lambda i: 200 if i>0 else 0)
    # Put new alpha channel back into original image and save
    img.putalpha(newA)
    return img


def put_on_template(template, pocasi):
    template.paste(pocasi, (0, 50), pocasi)
    template.save("pocasi.jpg")    


def put_sunrise_on_template(screen, template):
    sunrise = screen.crop((1176, 795, 1497, 851))
    
    # Putting sunrise on right corner
    pos_x = template.size[0] - sunrise.size[0]
    template.paste(sunrise, (pos_x, 0), sunrise)
    return template


def put_moon_on_template(screen, template):
    # Get moon phase image
    moon_page = requests.get("https://www.timeanddate.com/moon/phases/@3068294").text
    moon_img_link = moon_page.split("<img id=cur-moon src=")[1].split('\"')[1]
    
    # Process and resize image
    response = requests.get("https://www.timeanddate.com" + moon_img_link)
    moon = Image.open(BytesIO(response.content)).convert("RGBA").resize((60, 60))
    
    # Putting sunrise on right corner
    pos_x = template.size[0] - moon.size[0]
    template.paste(moon, (pos_x - 6, 62), moon)
    return template


def create_template():
    # Choosing random template
    template = Image.open(os.path.join("./img/templates", random.choice(os.listdir("./img/templates"))))

    sunrise_template = put_sunrise_on_template(screen, template)
    moon_template = put_moon_on_template(screen, sunrise_template)
    print("Pocasi modified")
    return moon_template


def get_client():
    cl = Client()
    cl.load_settings('dumped.json')
    #cl.login("zitrabude_", "Z&traB&de", verification_code=input("Code: "))  

    cl.dump_settings('dumped.json')
    
    print("Client logged")
    return cl


def post_weather(cl):
    weather_img = Path("pocasi.jpg")
    if os.name == 'nt':
        tmrw = (date.today() + timedelta(days=1)).strftime("%d. %m. %Y")   
    else:
        tmrw = (date.today() + timedelta(days=1)).strftime("%-d. %-m. %Y")   
    description = f"Zítra {tmrw} bude..."

    cl.photo_upload(weather_img, description)
    print("Photo uploaded")


def post_radar(cl):
    radar = Path("radar.mp4")

    cl.video_upload_to_story(radar)
    print("Radar story posted")


def get_radar():
    # Sets up selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=599,800")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)      
    some_wait_time = 5

    # Get image in browser
    url = "https://www.ventusky.com/?l=radar&w=0AAaAp92A"
    driver.get(url)

    # Change language
    menu = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.TAG_NAME, "menu"))
    )

    driver.execute_script("arguments[0].setAttribute('class','k')", menu)   
    time.sleep(some_wait_time)

    menu_settings = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "menu-settings"))
    ).click()

    time.sleep(some_wait_time)
    lang_select = Select(driver.find_elements(By.CLASS_NAME, 'resp_table_cell')[1].find_element(By.TAG_NAME, "select"))
    lang_select.select_by_value("cs")

    close = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "aside_close_btn_ico"))
    )
    
    action = ActionChains(driver)
    action.click(on_element = close)
    action.perform()

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "search-q"))
    ).send_keys("Czech republic")

    time.sleep(some_wait_time * 3)
    listed = driver.find_element(By.ID, "header").find_element(By.TAG_NAME, "ul")
    
    listed_item = None
    while not listed_item:
        try:
            listed_item = listed.find_element(By.TAG_NAME, "a")
        except Exception:
            print("Getting the czech republic from list")
        time.sleep(2)
        
    time.sleep(some_wait_time * 3)
    listed_item.click()
    
    # Zoom in
    driver.execute_script("const style = document.createElement('style');style.textContent = `.z { display: block !important; }`; document.head.appendChild(style);");
    driver.find_element(By.CLASS_NAME, "z").click()
    driver.execute_script("const style = document.createElement('style');style.textContent = `#header, menu, .z, .qw, #h { display: none !important; }`; document.head.appendChild(style);");

    # Screenshoting right times
    times = driver.find_element(By.CLASS_NAME, "ks").find_element(By.TAG_NAME, "ul")
    hour_now = datetime.now()
    for i in range(1, 10):
        next = hour_now + timedelta(hours=i)
        next_hour = "{:%H}".format(next)   

        print(f"Searching for {next_hour}")
        found = False
        while not found:
            time_elements = times.find_elements(By.TAG_NAME, "li")          

            for elem in time_elements:
                if "background: rgba(0, 0" not in elem.get_attribute("style"):
                    print(f"Now we have: {elem.text}")
                    time.sleep(some_wait_time)

                if elem.text == next_hour+":00" and "background: rgba(0, 0" not in elem.get_attribute("style"):
                    print("Found it: "+elem.text)
                    found = True
                    
                    time.sleep(some_wait_time)
                    driver.get_screenshot_as_file("img/radar/radar" + str(i) + ".png")

                    time.sleep(some_wait_time * 3)
                    print("Screenshot taken " + str(i))
                    break
            
            if found:
                break
            
            print("moving")
            time.sleep(some_wait_time)
            ActionChains(driver).move_to_element(time_elements[len(time_elements)-2]).click(time_elements[len(time_elements)-2]).perform()

    print("Pocasi saved")


def create_video():
    if os.name == 'nt':
        os.system('ffmpeg -framerate 1 -pattern_type sequence -start_number 00001 -i "./img/radar/radar%01d.png" -vcodec libx264  -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -r 24  -y -an radar.mp4')
    else:    
        os.system('ffmpeg -framerate 1 -pattern_type glob -i "./img/radar/*.png" -vcodec libx264  -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -r 24  -y -an radar.mp4')

if __name__ == "__main__":
    if datetime.now().hour < 10:
        get_radar()
        create_video()   

        random_wait = random.randint(30, 300)
        print(f"Waiting {random_wait} seconds to disguise bot")
        time.sleep(random_wait)

        cl = get_client()
        post_radar(cl)     
        
        os.remove("radar.mp4")
        os.remove("radar.mp4.jpg")
        
    else:     
        random_wait = random.randint(30, 300)
        print(f"Waiting {random_wait} seconds to disguise bot")
        time.sleep(random_wait)    
        
        # Get pocasi image
        screen = get_pocasi()

        # Modify the image
        pocasi_from_screen = crop_screen_img(screen)
        cropped_pocasi = crop_to_template(pocasi_from_screen)
        transparent_pocasi = change_opacity(cropped_pocasi)

        # Put it on template and save it
        put_on_template(create_template(), transparent_pocasi) 
        
        # Upload post to instagram
        cl = get_client()
        post_weather(cl)    
        
        # Removing img results
        os.remove("pocasi.jpg")
        os.remove("pocasi.png")
