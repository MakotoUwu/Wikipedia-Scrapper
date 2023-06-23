import json
import requests
from bs4 import BeautifulSoup
import re

def save(leaders_per_country):
    # Save leaders_per_country to leaders.json
    with open('leaders.json', 'w') as f:
        json.dump(leaders_per_country, f, indent=4, sort_keys=True)

def get_leaders():
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
            # Handle the error accordingly, e.g., retry or log the error.

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
        
    save(leaders_per_country)

    return leaders_per_country

def get_first_paragraph(session, wikipedia_url):
    # Code for retrieving the first paragraph from Wikipedia

    # Regular expressions to remove unwanted patterns from the paragraph
    regex_list = [
        r"\ *\(/.+/\[e\].*\)",  # Matches a pattern that starts with an optional space, followed by a forward slash, any character one or more times (except newline), followed by "/[e]", and then followed by any characters zero or more times.
        r"\ *\(/.+/.*\)",  # Matches a pattern that starts with an optional space, followed by a forward slash, any character one or more times (except newline), and then followed by any characters zero or more times.
        r"\[[0-9]+\]",  # Matches a pattern that starts with an opening square bracket, followed by one or more digits, and ends with a closing square bracket.
        r"[\n]",  # Matches a newline character.
        r"[\t]",  # Matches a tab character.
        r"[\xa0]"  # Matches a non-breaking space character.
    ]

    response = session.get(wikipedia_url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    
    for paragraph in soup.find_all('p'):
        if paragraph.text.strip():
            first_paragraph = paragraph.text.strip()

            for regex in regex_list:
                pattern = re.compile(regex)
                first_paragraph = re.sub(pattern, "", first_paragraph)
                
            break
    
    return first_paragraph



# Call the function (1 line)
result = get_leaders()
print(result)

# Read data from leaders.json
with open('leaders.json', 'r') as f:
    saved_leaders = json.load(f)

# Check if the variables match
print(saved_leaders == result)

