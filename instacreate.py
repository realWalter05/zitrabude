from instagrapi import Client
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageOps
import requests
import datetime
from io import BytesIO
import os
import random
import time


def create_instagram_account():
    # Sets up selenium
    chrome_options = Options()
#    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)      

    url = "https://www.instagram.com/accounts/emailsignup/?hl=en"
    driver.get(url)
    
    time.sleep(10)
    driver.find_element(By.XPATH, "//*[contains(text(), 'Allow essential and optional cookies')]").click()
    
    time.sleep(10)
    driver.find_elements(By.TAG_NAME, 'input')[0].send_keys("+420703340508")
    driver.find_elements(By.TAG_NAME, 'input')[1].send_keys("zitrabude")
    driver.find_elements(By.TAG_NAME, 'input')[2].send_keys("zitrabude_")
    driver.find_elements(By.TAG_NAME, 'input')[3].send_keys("@A&i#159324786")
    
    time.sleep(10)
    driver.find_element(By.XPATH, '//button[text()="Next"]').click()

    time.sleep(10)
    driver.find_elements(By.TAG_NAME, 'select')[0].send_keys("December")
    driver.find_elements(By.TAG_NAME, 'select')[1].send_keys("29")
    driver.find_elements(By.TAG_NAME, 'select')[2].send_keys("2000")

    time.sleep(10)
    driver.find_element(By.XPATH, '//button[text()="Next"]').click()    

    time.sleep(10)
    input_code = input("Verification code: ")
    driver.find_elements(By.TAG_NAME, 'input')[0].send_keys(input_code)

    time.sleep(10)
    driver.find_element(By.XPATH, '//button[text()="Confirm"]').click()       

    time.sleep(5)
    input("All done :)")


if __name__ == "__main__":
    create_instagram_account()