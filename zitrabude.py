from instagrapi import Client
from pathlib import Path
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageOps
import requests
import datetime
from io import BytesIO
import os
import random


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
    cl.login("zitrabude", "z&t#aBuDe9541593786")
    print("Client logged")
    return cl


def post_weather(cl):
    weather_img = Path("pocasi.jpg")

    tmrw = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%-d. %-m. %Y")
    description = f"Zítra {tmrw} bude..."

    cl.photo_upload(weather_img, description)
    print("Photo uploaded")


if __name__ == "__main__":
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

    # Removing images
    os.remove("pocasi.jpg")
    os.remove("pocasi.png")
