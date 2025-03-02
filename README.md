# LinkedIn Profile Scraper

## Overview
This Python script automates the process of scraping LinkedIn profiles from your connections. It logs into LinkedIn, navigates to the "My Network" section, extracts profile links, and retrieves details such as name, headline, experience, education, skills, email, and phone number (if available). The extracted data is saved in a JSON file for further use.

## Features
- **Automated Login**: Logs into LinkedIn using provided credentials.
- **Profile Extraction**: Extracts names, headlines, experience, education, and skills.
- **Contact Information**: Retrieves emails and phone numbers if available.
- **Scrolling and Navigation**: Loads additional connections dynamically.
- **Data Storage**: Saves extracted data into a JSON file.

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- Google Chrome browser
- Chrome WebDriver (Ensure compatibility with your Chrome version)
- Required Python libraries:
  ```bash
  pip install selenium beautifulsoup4 requests python-dotenv lxml
  ```

## Setup and Usage
### 1. Configure Environment Variables (Optional)
You can store your LinkedIn credentials in a `.env` file:
```env
EMAIL=your_email@example.com
PASSWORD=your_password
```
Uncomment the `load_dotenv()` line in the script to use the environment variables instead of hardcoding credentials.

### 2. Run the Script
- Open the terminal and navigate to the script directory.
- Execute the script using:
  ```bash
  python linkedin_scraper.py
  ```
- The script will log in, scrape profiles, and save the extracted data in `LinkedIn_profiles.json`.

## Extracted Data Format
The scraped data is stored in `LinkedIn_profiles.json` in the following format:
```json
[
    {
        "profile_url": "https://www.linkedin.com/in/example",
        "name": "John Doe",
        "headline": "Software Engineer at XYZ Corp",
        "about": "Experienced in web development...",
        "experience": [
            {
                "designation": "Senior Developer",
                "company_name": "XYZ Corp",
                "duration": "Jan 2020 - Present",
                "skills": ["Python", "Django", "REST API"]
            }
        ],
        "education": [
            {
                "institution": "ABC University",
                "course": "B.Tech in Computer Science",
                "duration": "2015 - 2019"
            }
        ],
        "email": "johndoe@example.com",
        "phone": "1234567890"
    }
]
```

## API Endpoints
If this scraper is converted into an API, the following endpoints can be used:

### 1. Scrape Profiles
**Endpoint:** `/scrape`
- **Method:** POST
- **Request Body:**
  ```json
  {
      "email": "your_email@example.com",
      "password": "your_password"
  }
  ```
- **Response:**
  ```json
  {
      "status": "success",
      "message": "Scraping started",
      "data": [ ... ]
  }
  ```

### 2. Get Scraped Profiles
**Endpoint:** `/get_profiles`
- **Method:** GET
- **Response:**
  ```json
  [
      {
          "profile_url": "https://www.linkedin.com/in/example",
          "name": "John Doe",
          "headline": "Software Engineer at XYZ Corp"
      }
  ]
  ```

## Development Guidelines
1. **Include a README file** with project setup instructions.
2. **Document API endpoints** in the README.
3. **Add basic unit test cases** to ensure functionality.
4. **Ensure readable code** with necessary comments for maintainability.

## Notes
- **LinkedIn's Anti-Scraping Measures**: Frequent requests may trigger bot detection. Random sleep intervals have been added to mimic human behavior.
- **Avoid Hardcoded Credentials**: Store credentials securely using environment variables.
- **Use a VPN or Proxy**: If scraping at scale, using proxies can help prevent blocking.

## Disclaimer
This script is for educational purposes only. Scraping LinkedIn without permission may violate their Terms of Service. Use responsibly and ensure compliance with LinkedIn policies.

