import warnings, random, json, re
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from bs4 import BeautifulSoup

def setup_driver():
    warnings.filterwarnings("ignore")
    load_dotenv()
    chrome_options = Options()
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
    driver = webdriver.Chrome(options=chrome_options)
    return driver, WebDriverWait(driver, 10)

def login(driver, wait, email, password):
    driver.get('https://www.linkedin.com/login')
    time.sleep(random.uniform(3, 7))
    email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    password_input = driver.find_element(By.ID, "password")
    email_input.send_keys(email)
    time.sleep(random.uniform(2, 5))
    password_input.send_keys(password)
    password_input.submit()
    time.sleep(random.uniform(4, 8))

def navigate_to_connections(driver, wait):
    try:
        my_network = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/mynetwork/')]")))
        my_network.click()
        connections_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'connections')]")))
        connections_tab.click()
        driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
        time.sleep(random.uniform(3, 6))
    except Exception as e:
        print(f"Error navigating to Connections: {e}")
        driver.quit()
        exit()

def scroll_to_load(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_profile_links(driver):
    total_connections = driver.find_elements(By.XPATH, "//a[contains(@class, 'mn-connection-card__link')]")
    return [conn.get_attribute("href") for conn in total_connections[:10] if "linkedin.com/in/" in conn.get_attribute("href")]

def extract_profile_details(driver, wait, link):
    driver.get(link)
    time.sleep(random.uniform(3, 6))
    profile_data = {"profile_url": link, "experience": [], "education": []}
    
    try:
        profile_name = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class, 'artdeco-hoverable-trigger')]/ancestor::div[3]//h1"))).text
        profile_data["name"] = profile_name
    except:
        profile_data["name"] = "Not found"
    
    try:
        title = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]"))).text
        profile_data["headline"] = title
    except:
        profile_data["headline"] = "Not found"
    
    try:
        about_text = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'display-flex ph5 pv3')]"))).text.strip()
        profile_data["about"] = about_text
    except:
        profile_data["about"] = "Not Available"
    
    extract_experience_and_education(driver, profile_data)
    extract_contact_info(driver, profile_data, link)
    
    return profile_data

def extract_experience_and_education(driver, profile_data):
    soup = BeautifulSoup(driver.page_source, "lxml")
    sections = soup.find_all("section", class_="artdeco-card pv-profile-card break-words mt2")
    
    for sec in sections:
        if sec.find("div", id="experience"):
            for exp in sec.find_all("div", class_="display-flex flex-column align-self-center flex-grow-1"):
                try:
                    designation = exp.find("span", {"aria-hidden": "true"}).text.strip()
                    company_name = exp.find("span", class_="t-14 t-normal").find_next("span", {"aria-hidden": "true"}).text.strip().split(" · ")[0]
                    duration = exp.find("span", class_="pvs-entity__caption-wrapper").text.strip()
                    skills_link_element = exp.find("a",
                                                       class_="optional-action-target-wrapper display-flex link-without-hover-visited")
                    skills_link = skills_link_element["href"] if skills_link_element else None

                    extracted_skills = []

                    if skills_link:
                        driver.get(skills_link)
                        time.sleep(5)

                        # Wait for Modal Load
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "artdeco-modal__content")))

                        skills_page = driver.page_source

                        skill_soup = BeautifulSoup(skills_page, "lxml")
                        target_sec = skill_soup.find('ul').find('li').find('ul').find_all("li")  # step 1
                        for section in target_sec:
                            skill_text = section.find('span', class_='visually-hidden').text.strip()  # step 2
                            print(skill_text)
                            if skill_text:
                                extracted_skills.append(skill_text)

                        print(f"Extracted skills for {designation}: {extracted_skills}")
                    profile_data["experience"].append({"designation": designation, "company_name": company_name, "duration": duration,"skills": extracted_skills})

                except:
                    continue
        
        if sec.find("div", id="education"):
            for edu in sec.find_all("div", class_="display-flex flex-column align-self-center flex-grow-1"):
                try:
                    institution = edu.find("span", {"aria-hidden": "true"}).text.strip()
                    course = edu.find("span", class_="t-14 t-normal").find_next("span", {"aria-hidden": "true"}).text.strip().split(" · ")[0]
                    duration = edu.find("span", class_="pvs-entity__caption-wrapper").text.strip()
                    profile_data["education"].append({"institution": institution, "course": course, "duration": duration})
                except:
                    continue

def extract_contact_info(driver, profile_data, link):
    driver.get(f"{link}overlay/contact-info/")
    try:
        email_element = driver.find_element(By.XPATH, "//section[contains(@class, 'pv-contact-info__contact-type')]//a[contains(@href, 'mailto:')]")
        profile_data["email"] = email_element.text
    except:
        profile_data["email"] = "Email Not Found"
    
    try:
        phone_number = ''
        phone_section = driver.find_elements(By.XPATH, "//section[contains(@class, 'pv-contact-info__contact-type')]")
        for find_phone_num in phone_section:
            if 'Phone' in find_phone_num.text:
                phone_number = re.search('\d{10}', find_phone_num.text).group()
                profile_data["phone"] = phone_number
            else:
                phone_number = 'Not Available'

    except:
        phone_number = "Phone Number Not Available"

def main():
    driver, wait = setup_driver()
    email, password = os.getenv("EMAIL"), os.getenv("PASSWORD")
    login(driver, wait, email, password)
    navigate_to_connections(driver, wait)
    scroll_to_load(driver)
    profile_links = extract_profile_links(driver)
    
    profiles = []
    for link in profile_links:
        profiles.append(extract_profile_details(driver, wait, link))
        time.sleep(random.randint(50, 100))
    
    with open("LinkedIn_profiles.json", "w", encoding="utf-8") as json_file:
        json.dump(profiles, json_file, indent=4, ensure_ascii=False)
    
    driver.quit()
    print("Data saved to LinkedIn_profiles.json")

if __name__ == "__main__":
    main()
