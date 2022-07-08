from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import autoit
import os
import time

# Sets up selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)  

def get_pocasi():
    url = "https://ct24.ceskatelevize.cz/pocasi/zitra"
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 250);")
    driver.get_screenshot_as_file("pocasi.png")

if __name__ == "__main__":
    print("Bot zitrabude has started")

    get_pocasi()

    url = "https://www.instagram.com/?hl=cs"
    driver.get(url)
    
    time.sleep(2)
    cookies = driver.find_element(By.XPATH, "//*[text()='Povolit jen nezbytné soubory cookie']")
    cookies.click()
    
    time.sleep(2)
    username = driver.find_element(By.NAME, "username")
    username.send_keys("zitrabude")

    password = driver.find_element(By.NAME, "password")
    password.send_keys("z&t#aBuDe9541593786")

    login_btn = driver.find_element(By.XPATH, "//*[text()='Přihlásit se']")
    login_btn.click()    

    time.sleep(5)
    save_login_btn = driver.find_element(By.XPATH, "//*[text()='Uložit informace']")
    save_login_btn.click()

    time.sleep(5)
    notifications_btn = driver.find_element(By.XPATH, "//*[text()='Not Now']")
    notifications_btn.click()

    create_post_div = driver.find_elements(By.CSS_SELECTOR, "._acus ._acut")
    create_post_div[2].click()    

    time.sleep(2)
    create_post_btn = driver.find_element(By.XPATH, "//*[text()='Select from computer']")
    create_post_btn.click()
    
    time.sleep(2)
    autoit.win_active("Open")
    autoit.control_set_text("Open","Edit1",r"C:\Users\Walter\Desktop\Python\zitrabude\pocasi.png")
    autoit.control_send("Open","Edit1","{ENTER}")

    time.sleep(2)
    next_btn = driver.find_element(By.XPATH, "//*[text()='Next']")
    next_btn.click()

    time.sleep(2)
    next1_btn = driver.find_element(By.XPATH, "//*[text()='Next']")
    next1_btn.click()

    time.sleep(2)
    shate_btn = driver.find_element(By.XPATH, "//*[text()='Share']")
    shate_btn.click()        

    #input("Press enter to close browser: ")
    driver.quit()
    os.remove("pocasi.png")