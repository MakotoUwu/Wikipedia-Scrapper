import requests
from bs4 import BeautifulSoup
import re

def query_status():
    # Import the requests library
    import requests

    # Set the root URL
    root_url = "https://country-leaders.onrender.com"

    # Set the status URL
    status_url = root_url + "/status"

    # Query the status endpoint
    req = requests.get(status_url)

    # Check the status code and print appropriate messages
    if req.status_code == 200:
        print(req.text)
    else:
        print("Status Code:", req.status_code)

def query_countries():
    # Set the countries URL
    countries_url = "https://country-leaders.onrender.com/countries"

    # Query the countries endpoint
    req = requests.get(countries_url)

    # Get the JSON content
    countries = req.json()

    # Display the status code and countries
    print("Status Code:", req.status_code)
    #print(countries)

def get_cookie():
    # Set the cookie URL
    cookie_url = "https://country-leaders.onrender.com/cookie"

    # Query the cookie endpoint
    req = requests.get(cookie_url)

    # Extract the appropriate field from the response
    cookies = req.cookies.get("country-leaders")

    # Display the cookie
    #print(cookies)

def query_leaders():
    # Set the leaders URL
    leaders_url = "https://country-leaders.onrender.com/leaders"

    # Query the leaders endpoint
    req = requests.get(leaders_url)

    # Display the leaders
    #print(req.json())

def get_leaders():
    # Define the URLs
    root_url = "https://country-leaders.onrender.com"
    status_url = root_url + "/status"
    countries_url = root_url + "/countries"
    cookie_url = root_url + "/cookie"
    leaders_url = root_url + "/leaders"
    leaders_per_country = {}

    # Get the cookies
    cookies = requests.get(cookie_url).cookies

    # Get the countries
    countries = requests.get(countries_url, cookies=cookies).json()

    for country in countries:
        leaders = requests.get(leaders_url, cookies=cookies, params={"country": country}).json()
        leaders_per_country[country] = leaders

    return leaders_per_country

def get_first_paragraph(wikipedia_url):
    print(wikipedia_url)
    response = requests.get(wikipedia_url)
    html_text = response.text
    soup = BeautifulSoup(html_text, "html.parser")
    paragraphs = soup.find_all("p")
    first_paragraph = ""

    for p in paragraphs:
        if p.text.strip():
            first_paragraph = p.text
            break
    
    #Remove references like [1], [2], etc.
    

    #Remove HTML tags like <sup>, </sup>, etc.
    first_paragraph = re.sub(r"<[^>]+>", "", first_paragraph)

    #Remove phonetic pronunciation like /ˈdʒoʊzəf/, etc.
    first_paragraph = re.sub(r"/[^/]+/", "", first_paragraph)

    return first_paragraph

# Query the status endpoint
query_status()

# Query the countries endpoint
query_countries()

# Query the cookie endpoint
get_cookie()

# Query the leaders endpoint
query_leaders()

# Get the leaders per country
leaders_per_country = get_leaders()
#print(leaders_per_country)

# Test get_first_paragraph function
wikipedia_url = "https://en.wikipedia.org/wiki/Joe_Biden"
first_paragraph = get_first_paragraph(wikipedia_url)
print(first_paragraph)



#API Scraping

""" def check(status):
    req = requests.get(status)

    if req.status_code == 200: 
        print(req.text) 
    else: 
        print(req.status_code)

#dealing with JSON

check_url = check(status_url)
#можна зробити перевірку що якщо немає реквеста то не йти далі
countries = requests.get(root_url + countries_url).json()

print("Status code: ", req.status_code, " Countries: ", countries)

#Cookies anyone?


cookies = requests.get(cookie_url).cookies
print("Cookies: ", cookies)



print("Countries: ", countries)

#Getting the actual data from the API


leaders = requests.get(leaders_url).json()
print("Leaders: ", leaders)

#Change the query to accept parameters. You should know where to find help by now.
leaders = requests.get(leaders_url, cookies=cookies, params={"country": "be"}).json()

print("Leaders: ", leaders)
 """

#A sneak peak at the data (finally)