from fastapi import FastAPI, HTTPException, Depends
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict
import time
import random

app = FastAPI()

# LinkedIn Credentials (Replace with environment variables or config management)
EMAIL = "testingcase0405@gmail.com"
PASSWORD = "Testing1234@"

# Chrome options for Selenium
chrome_options = Options()

chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--incognito")

chrome_options.add_argument("--disable-webrtc")
chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")

# Session Persistence
session = requests.Session()
COOKIES = None
CSRF_TOKEN = None
LI_AT = None

# Voyager API URL
VOYAGER_API_URL = "https://www.linkedin.com/voyager/api/relationships/connections"

# Function to log in and fetch session cookies
def login_linkedin():
    global COOKIES, CSRF_TOKEN, LI_AT
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.linkedin.com/login")
    time.sleep(random.uniform(3, 7))
    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    password_input = driver.find_element(By.ID, "password")
    email_input.send_keys(EMAIL)
    time.sleep(random.uniform(2, 5))
    password_input.send_keys(PASSWORD)
    password_input.submit()
    time.sleep(random.uniform(4, 8))
    cookies = driver.get_cookies()
    driver.quit()
    session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    COOKIES = session_cookies
    CSRF_TOKEN = session_cookies.get("JSESSIONID", "").replace('"', '')
    LI_AT = session_cookies.get("li_at","").replace('"','')
    return session_cookies


# Function to fetch LinkedIn connections
def fetch_connections():
    if not COOKIES:
        login_linkedin()
   
    headers = {
        'authority': 'www.linkedin.com',
        'accept': 'application/vnd.linkedin.normalized+json+2.1',
        'csrf-token': f"ajax:{CSRF_TOKEN}",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'referer': 'https://www.linkedin.com/mynetwork/invite-connect/connections/',
        'x-li-lang': 'en_US',
        'x-restli-protocol-version': '2.0.0',
    }
    cookies = {
        'li_at': LI_AT,
        'JSESSIONID': f"ajax:{CSRF_TOKEN}",
    }
    response = session.get(VOYAGER_API_URL, headers=headers,cookies=cookies)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch LinkedIn data")
    data = response.json()
    connections = []
    for item in data.get("elements", []):
        profile = {
            "profile_url": f"https://www.linkedin.com/in/{item.get('publicIdentifier')}",
            "name": item.get("firstName") + " " + item.get("lastName"),
            "headline": item.get("headline", "N/A"),
            "email": item.get("email", "N/A")
        }
        connections.append(profile)
    return {"connections": connections}
@app.get("/connections")
def get_linkedin_connections():
    return fetch_connections()