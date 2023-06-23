import json
import requests
from bs4 import BeautifulSoup
import re
import time

def greet_user():
    """
    Displays a greeting message, and explains the purpose of this script to the user.
    """
    print("\n===============================")
    print("Hello! Welcome to our scraper!")
    print("===============================")

    print("""
      / _ \\
    \\_\\(_)/_/
     _//"\\\\_  
      /   \\ 
    """)
    
    print("Scattering our cobwebs...") 
    print("Please wait while we are scraping the data...\n")


def save(leaders_per_country):
    """
    Saves the leaders' data to a json file, replacing None values with 'Unknown information'
    """
    # Replace None values with a default string
    for country in leaders_per_country:
        for leader in leaders_per_country[country]:
            for key, value in leader.items():
                if value is None:
                    leader[key] = 'Unknown information'

    # Save leaders_per_country to leaders.json
    with open('leaders.json', 'w', encoding='utf-8') as f:
        json.dump(leaders_per_country, f, indent=4, sort_keys=True, ensure_ascii=False)

def get_leaders():
    """
    Retrieves leaders' data from the given URL and stores them in a dictionary.
    Also handles session cookies and HTTP errors.
    """
    # Define the URLs
    root_url = "https://country-leaders.onrender.com"
    countries_url = root_url + "/countries"
    leaders_url = root_url + "/leaders"
    cookie_url = root_url + "/cookie"

    # Create a session
    session = requests.Session()

    # Get the initial cookies
    cookies = session.get(cookie_url).cookies

    # Get the countries
    countries_response = session.get(countries_url, cookies=cookies)

    # Check if there is a cookie error
    if countries_response.status_code == 401:
        # Get new cookies
        cookies = session.get(cookie_url).cookies
        countries_response = session.get(countries_url, cookies=cookies)

    # Check if there is an exception or another error
    countries_response.raise_for_status()

    countries = countries_response.json()

    # Create an empty dictionary
    leaders_per_country = {}

    start_time = time.time()  # Start the timer

    # Loop through the countries
    for country in countries:
        params = {"country": country}
        leaders_response = None

        try:
            leaders_response = session.get(leaders_url, cookies=cookies, params=params)

            # Retry with new cookies if a "403 Forbidden" error occurs
            while leaders_response.status_code == 403:
                # Get new cookies
                cookies = session.get(cookie_url).cookies
                leaders_response = session.get(leaders_url, cookies=cookies, params=params)

            # Check if there is an exception or another error
            leaders_response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            print("An error occurred:", e)

        if leaders_response is not None:
            leaders = leaders_response.json()
            leaders_with_paragraph = []

            # Loop through the leaders of each country
            for leader in leaders:
                leader_url = leader["wikipedia_url"]
                leader_first_paragraph = get_first_paragraph(session, leader_url)

                leader_with_paragraph = leader.copy()
                leader_with_paragraph["first_paragraph"] = leader_first_paragraph
                leaders_with_paragraph.append(leader_with_paragraph)

            leaders_per_country[country] = leaders_with_paragraph

            # Display message to the user
            elapsed_time = time.time() - start_time
            print(f"Scraped leaders for {country}. Elapsed time: {elapsed_time:.2f} seconds.")
            time.sleep(1)  # Pause for 1 second to simulate processing time
        
    save(leaders_per_country)

    print("\nLeaders scraping completed.")
    print("Your JSON file is ready.")

    return leaders_per_country

def get_first_paragraph(session, wikipedia_url):
    """
    Retrieves and cleans the first paragraph from a given Wikipedia page
    """
    # Regular expressions to remove unwanted patterns from the paragraph
    regex_list = [
        r"\ *\(/.+/\[e\].*\)", # Matches any text within parentheses with "/[e]" inside and optionally preceded by a space
        r"\ *\(/.+/.*\)", # Matches any text within parentheses optionally preceded by a space
        r"\[[0-9]+\]", # Matches any text within square brackets that contains one or more digits
        r"[\n]", # Matches a newline character
        r"[\t]", # Matches a tab character
        r"[\xa0]", # Matches a non-breaking space character
        r"\[[^\]]*\]", # Matches any text within square brackets excluding the brackets
        r"\(.*?\)", # Matches any text within parentheses
        r'\\\"'  # Matches occurrences of \"
    ]

    response = session.get(wikipedia_url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # Parse through the HTML using BeautifulSoup and extract the first paragraph of the article
    for paragraph in soup.find_all('p'):
        if paragraph.text.strip():
            first_paragraph = paragraph.text.strip()

            # Clean the first paragraph using the regular expressions defined above
            for regex in regex_list:
                pattern = re.compile(regex)
                first_paragraph = re.sub(pattern, "", first_paragraph)

            break

    return first_paragraph

def check_scraping():
    greet_user()

    # Scrape the data again
    scraped_leaders = get_leaders()

     # Read data from leaders.json
    with open('leaders.json', 'r', encoding = "utf-8") as f:
        saved_leaders = json.load(f)

    # Check if the variables match
    if saved_leaders == scraped_leaders:
        print("\nSuccess! Scraping matched the saved data.")
    else:
        print("Error! Scraping didn't match the saved data. Try again.")
    return saved_leaders == scraped_leaders

result = check_scraping()