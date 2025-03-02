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

# Ignore warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()
email_id = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


# Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-webrtc")
chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# Open LinkedIn Login Page
driver.get('https://www.linkedin.com/login')
time.sleep(random.uniform(3, 7))

# Login to LinkedIn
email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
password_input = driver.find_element(By.ID, "password")

email_input.send_keys(email_id)
time.sleep(random.uniform(2, 5))
password_input.send_keys(password)
password_input.submit()
time.sleep(random.uniform(4, 8)) # ipova

# Navigate to "My Network"
try:
    my_network = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/mynetwork/')]")))
    my_network.click()
except Exception as e:
    print(f"Error clicking 'My Network': {e}")
    driver.quit()
    exit()

# Wait for Connections tab to load
try:
    connections_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'connections')]")))
    connections_tab.click()
except Exception as e:
    print(f"Error clicking 'Connections': {e}")
    driver.quit()
    exit()

# Ensure the connections page loads
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
time.sleep(random.uniform(3, 6))

# Scroll down to load more connections
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for new connections to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:  # Stop when no new content loads
        break
    last_height = new_height

# Wait until connection elements are loaded
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mn-connection-card__name")))

# Click each connection link and extract details
total_connections = driver.find_elements(By.XPATH, "//a[contains(@class, 'mn-connection-card__link')]")

profile_links = []
for index, connection_ in enumerate(total_connections):
    profile_url = connection_.get_attribute("href")
    if profile_url and "linkedin.com/in/" in profile_url:
        profile_links.append(profile_url)
    if index == 9:
        break

print('profile_links: ', len(profile_links))
print("\nExtracted Profile Links:")
profiles = []

for link in profile_links:
    driver.get(link)
    time.sleep(random.uniform(3, 6))
    profile_data = {"profile_url": link, "experience": [], "education": []}
    # Extract Profile Name
    try:
        profile_name = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class, 'artdeco-hoverable-trigger')]/ancestor::div[3]//h1"))).text
        profile_data["name"] = profile_name
    except:
        profile_name = "Not found"

    # **Extract Title**
    try:
        title = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]"))).text
        profile_data["headline"] = title
    except:
        title = "Not found"
    print(title)

    try:
        see_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'inline-show-more-text__button')]"))
        )
        driver.execute_script("arguments[0].click();", see_more_button)
        time.sleep(2)
    except:
        pass  # If button is not found, continue

    # Extract "About" Section
    try:
        about_text = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'display-flex ph5 pv3')]")))
        profile_data["about"] = about_text.text.strip()
    except:
        profile_data["about"] = "Not Available"

    print(f"Profile: {profile_name}")
    print(f"title: {title}")

    # Extract Experience Details

    try:
        page_source = driver.page_source
        soup_content = BeautifulSoup(page_source, "lxml")
        all_sections = soup_content.find_all("section", class_="artdeco-card pv-profile-card break-words mt2")
        for sec in all_sections:
            if sec.find("div", id="experience"):
                all_experience = sec.find_all("div", class_="display-flex flex-column align-self-center flex-grow-1")
                print(f"Found {len(all_experience)} experience entries")  # Debugging
                for exp in all_experience:
                    try:
                        designation = exp.find("div", class_="display-flex flex-wrap align-items-center full-height") \
                            .find("span", {"aria-hidden": "true"}).text.strip()
                        company_name = exp.find("span", class_="t-14 t-normal") \
                            .find_next("span", {"aria-hidden": "true"}).text.strip().split(" · ")[0]
                        duration = exp.find("span", class_="pvs-entity__caption-wrapper").text.strip()

                        # Get Skills Link (Safely)
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

                            print(f"Extracted skills for {designation}: {extracted_skills}")  # Debugging

                        # Append experience only if extraction is successful
                        profile_data["experience"].append({
                            "designation": designation,
                            "company_name": company_name,
                            "duration": duration,
                            "skills": extracted_skills
                        })

                    except Exception as e:
                        print(f"Error extracting experience entry: {e}")  # Debugging

            if sec.find('div', id='education'):
                all_education = sec.find_all("div", class_="display-flex flex-column align-self-center flex-grow-1")
                print(f"Found {len(all_education)} experience entries")
                for edu in all_education:
                    # print(edu)
                    try:
                        edc_name = edu.find("div", class_="display-flex flex-wrap align-items-center full-height") \
                            .find("span", {"aria-hidden": "true"}).text.strip()
                        course_name = edu.find("span", class_="t-14 t-normal") \
                            .find_next("span", {"aria-hidden": "true"}).text.strip().split(" · ")[0]
                        course_duration = edu.find("span", class_="pvs-entity__caption-wrapper").text.strip()
                        print('edc_name==>', edc_name)
                        print('course_name==>', course_name)
                        print('course_duration==>', course_duration)
                        profile_data["education"].append({
                            "institution": edc_name,
                            "course": course_name,
                            "duration": course_duration
                        })
                        # print(profile_data)
                    except Exception as e:
                        print(f"Error extracting experience entry: {e}")  # Debugging


    except Exception as e:
        print(f"Error extracting experience section: {e}")

    # Close browser

    # Extract Contact Info
    contact_link = f"{link}overlay/contact-info/"
    driver.get(contact_link)

    # Extract Email
    try:
        email_element = driver.find_element(By.XPATH,
                                            "//section[contains(@class, 'pv-contact-info__contact-type')]//a[contains(@href, 'mailto:')]")
        email = email_element.text
        profile_data["email"] = email
    except:
        email = "Email Not Found"

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

    # Save profile data to a JSON file
    profiles.append(profile_data)
    sleep_time = random.randint(60, 240)
    time.sleep(sleep_time)
output_file = "LinkedIn_profiles.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(profiles, json_file, indent=4, ensure_ascii=False)

print(f"Data saved to {output_file}")

time.sleep(random.uniform(3, 6))

driver.quit()
