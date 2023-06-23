import json
import requests
from bs4 import BeautifulSoup
import re
import time

def greet_user():
    """
    Displays a greeting messages to the user.
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
    
    print("Scattering our cobwebs...\n") 
    print("Please wait while we are scraping the data...\n")


def save(leaders_per_country):
    """
    Function to save the leaders' data to a JSON file.
    It replaces all None values with a placeholder string 'Unknown information'.
    """
    # Loop over the countries in the leaders_per_country dictionary
    for country in leaders_per_country:
        # Loop over the leaders in the current country
        for leader in leaders_per_country[country]:
            # Loop over the attributes of the current leader
            for key, value in leader.items():
                # If an attribute's value is None, replace it with a default string
                if value is None:
                    leader[key] = 'Unknown information'

    # Save the leaders_per_country dictionary to a JSON file
    with open('leaders.json', 'w', encoding='utf-8') as f:
        # dump() function writes the Python dictionary to the JSON file
        # indent=4 makes the file human-readable with 4 spaces of indentation
        # sort_keys=True sorts the keys alphabetically
        # ensure_ascii=False ensures that non-ASCII characters are saved correctly
        json.dump(leaders_per_country, f, indent=4, sort_keys=True, ensure_ascii=False)


def get_leaders():
    """
    Function to retrieve leaders' data from a predefined website.
    It manages session cookies, HTTP errors, and stores the resulting data into a dictionary.
    """
    # Set the root, countries, leaders, and cookie URLs
    root_url = "https://country-leaders.onrender.com"
    countries_url = root_url + "/countries"
    leaders_url = root_url + "/leaders"
    cookie_url = root_url + "/cookie"

    # Create a web session using requests.Session()
    session = requests.Session()

    # Retrieve the initial cookies from the cookie URL
    cookies = session.get(cookie_url).cookies

    # Get the list of countries from the countries URL
    countries_response = session.get(countries_url, cookies=cookies)

    # If an authorization error (401) occurs, refresh the cookies and try again
    if countries_response.status_code == 401:
        cookies = session.get(cookie_url).cookies
        countries_response = session.get(countries_url, cookies=cookies)

    # If there's any other kind of error, raise an exception
    countries_response.raise_for_status()

    # Convert the response to JSON format
    countries = countries_response.json()

    # Initialize an empty dictionary to store the leaders
    leaders_per_country = {}

    start_time = time.time()  # Start the timer for performance tracking

    # Loop through the list of countries
    for country in countries:
        params = {"country": country}
        leaders_response = None

        try:
            # Try to get the leaders for the current country
            leaders_response = session.get(leaders_url, cookies=cookies, params=params)

            # If a "403 Forbidden" error occurs, refresh the cookies and try again
            while leaders_response.status_code == 403:
                cookies = session.get(cookie_url).cookies
                leaders_response = session.get(leaders_url, cookies=cookies, params=params)

            # If there's any other kind of error, raise an exception
            leaders_response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            # If an HTTP error occurs, print the error and continue with the next country
            print("An error occurred:", e)

        # If the response is successful, process the leaders
        if leaders_response is not None:
            leaders = leaders_response.json()
            leaders_with_paragraph = []

            # For each leader, get their Wikipedia first paragraph, add it to their dictionary, and append to the list
            for leader in leaders:
                leader_url = leader["wikipedia_url"]
                leader_first_paragraph = get_first_paragraph(session, leader_url)

                leader_with_paragraph = leader.copy()
                leader_with_paragraph["first_paragraph"] = leader_first_paragraph
                leaders_with_paragraph.append(leader_with_paragraph)

            # Add the list of leaders to the dictionary under the current country
            leaders_per_country[country] = leaders_with_paragraph

            # Print the progress for the user
            elapsed_time = time.time() - start_time
            print(f"Scraped leaders for {country}. Elapsed time: {elapsed_time:.2f} seconds.")
            time.sleep(1)  # Pause for 1 second to simulate processing time

    # Save the final dictionary to a file
    save(leaders_per_country)

    print("\nLeaders scraping completed.")
    print("Your JSON file is ready.")

    # Return the final dictionary
    return leaders_per_country


def get_first_paragraph(session, wikipedia_url):
    """
    Function that retrieves the first meaningful paragraph from a Wikipedia page and performs a clean-up
    operation to remove unwanted patterns.
    """

    # List of regular expressions to be used for cleaning the paragraph.
    # Each regex is aimed at removing a specific unwanted pattern.
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

    # Request the content of the webpage
    response = session.get(wikipedia_url)
    html = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Loop through all the paragraphs in the parsed HTML
    # The goal is to find the first meaningful (non-empty) paragraph
    for paragraph in soup.find_all('p'):
        if paragraph.text.strip():  # If the paragraph is not empty (has meaningful content)
            first_paragraph = paragraph.text.strip()

            # Clean the first paragraph by removing all unwanted patterns
            # This is done by substituting each matching pattern with an empty string
            for regex in regex_list:
                pattern = re.compile(regex)
                first_paragraph = re.sub(pattern, "", first_paragraph)

            # Once we have our first meaningful paragraph, exit the loop
            break

    # Return the cleaned first paragraph
    return first_paragraph


def check_scraping(): 
    """
    Function that performs the whole scraping process, validates the scraped data with the saved data, 
    and finally returns whether the scraping was successful.
    """

    # Display greeting message and explain the purpose of this script
    greet_user()

    # Scrape the leaders' data
    scraped_leaders = get_leaders()

    # Open 'leaders.json' file in read mode and load its data
    with open('leaders.json', 'r', encoding = "utf-8") as f:
        saved_leaders = json.load(f)

    # Check if the scraped data matches the saved data
    if saved_leaders == scraped_leaders:
        # If they match, print a success message
        print("\nSuccess! Scraping matched the saved data.\n")
    else:
        # If they don't match, print an error message
        print("Error! Scraping didn't match the saved data. Try again.")

    # Return True if the scraped data matches the saved data, else False
    return saved_leaders == scraped_leaders
