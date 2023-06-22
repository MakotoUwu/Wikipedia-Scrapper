# Import necessary libraries
import requests
import json
from bs4 import BeautifulSoup
import re

# Function to get leaders for each country
def get_leaders():
    # Define the urls
    root_url = 'https://country-leaders.onrender.com'
    status_url = root_url + '/status'
    countries_url = root_url + '/countries'
    leaders_url = root_url + '/leaders'
    cookie_url = root_url + '/cookie'

    # Get the cookies
    cookies = requests.get(cookie_url).cookies

    # Get the countries
    req = requests.get(countries_url, cookies=cookies)
    countries = req.json()

    # Initialize a dictionary to hold leader data
    leaders_per_country = {}

    # Initialize session
    with requests.Session() as s:
        # Loop over the countries and save their leaders in a dictionary
        for country in countries:
            try:
                response = s.get(leaders_url + '?country=' + country, cookies=cookies)
                response.raise_for_status()  # Check for HTTP errors
                leaders = response.json()
                
                # Get Wikipedia info for each leader
                for leader in leaders:
                    if 'wikipedia' in leader:
                        leader['first_paragraph'] = get_first_paragraph(leader['wikipedia'], s)

                leaders_per_country[country] = leaders
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 403:  # If cookie error
                    cookies = requests.get(cookie_url).cookies
                    response = s.get(leaders_url + '?country=' + country, cookies=cookies)
                    leaders = response.json()
                    
                    # Get Wikipedia info for each leader
                    for leader in leaders:
                        if 'wikipedia' in leader:
                            leader['first_paragraph'] = get_first_paragraph(leader['wikipedia'], s)

                    leaders_per_country[country] = leaders
                else:
                    print(f"HTTP error occurred: {err}")
    return leaders_per_country


# Function to get first paragraph from Wikipedia
def get_first_paragraph(wikipedia_url, session):
    response = session.get(wikipedia_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    first_paragraph = ''
    for para in paragraphs:
        if para.text and len(para.text) > 100:
            first_paragraph = re.sub(r'\[[^]]*\]', '', para.text)  # Remove references like [1]
            break
    return first_paragraph

# Function to save data into a json file
def save(data, filename='leaders.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Main function to get leaders and save data into a file
def main():
    leaders = get_leaders()
    save(leaders)

# Calling the main function
if __name__ == "__main__":
    main()
