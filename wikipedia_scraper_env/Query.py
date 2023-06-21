# Import the requests and BeautifulSoup libraries
import requests
from bs4 import BeautifulSoup

# Define the root url and the endpoints
root_url = "https://country-leaders.onrender.com"
status_url = root_url + "/status"
cookie_url = root_url + "/cookie"
countries_url = root_url + "/countries"
leaders_url = root_url + "/leaders"

# Define a function to get the first paragraph from a Wikipedia url
def get_first_paragraph(wikipedia_url):
    # Use requests to get the HTML content of the url
    response = requests.get(wikipedia_url)
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    # Find all the HTML paragraphs in the soup
    paragraphs = soup.find_all("p")
    # Loop over the paragraphs and look for the one that contains the leader's name
    for paragraph in paragraphs:
        # Get the text of the paragraph
        text = paragraph.get_text()
        # Check if the text contains "[name] (" where name is the leader's name
        if "[" + wikipedia_url.split("/")[-1] + " (" in text:
            # Remove any references, HTML tags, or phonetic pronunciations from the text using regular expressions
            text = re.sub(r"\[.*?\]", "", text) # remove references like [1], [2], etc.
            text = re.sub(r"<.*?>", "", text) # remove HTML tags like <br>, <sup>, etc.
            text = re.sub(r"\(.*?\)", "", text) # remove phonetic pronunciations like (listen), (French: ...), etc.
            # Return the sanitized text as the first paragraph
            return text

# Define a function to get all the leaders per country from the API and Wikipedia
def get_leaders():
    # Create an empty dictionary to store the leaders per country
    leaders_per_country = {}
    # Use requests to get a cookie from the API
    cookie_response = requests.get(cookie_url)
    # Extract the cookie value from the response
    cookie_value = cookie_response.json()["cookie"]
    # Set the cookie as a header for future requests
    headers = {"Cookie": cookie_value}
    # Use requests to get the list of countries from the API with the cookie header
    countries_response = requests.get(countries_url, headers=headers)
    # Extract the list of countries from the response
    countries = countries_response.json()["countries"]
    # Loop over each country in the list
    for country in countries:
        # Use requests to get the list of leaders for that country from the API with the cookie header and the country parameter
        leaders_response = requests.get(leaders_url, headers=headers, params={"country": country})
        # Extract the list of leaders from the response
        leaders = leaders_response.json()["leaders"]
        # Create an empty list to store the updated leaders for that country
        updated_leaders = []
        # Loop over each leader in the list
        for leader in leaders:
            # Get the Wikipedia url for that leader
            wikipedia_url = leader["wikipedia"]
            # Use the get_first_paragraph function to get the first paragraph from that url
            first_paragraph = get_first_paragraph(wikipedia_url)
            # Update the leader's dictionary with a new key-value pair for the first paragraph
            leader["first_paragraph"] = first_paragraph
            # Append the updated leader to the updated leaders list
            updated_leaders.append(leader)
        # Update the leaders per country dictionary with a new key-value pair for that country and its updated leaders list
        leaders_per_country[country] = updated_leaders
    # Return the leaders per country dictionary
    return leaders_per_country

# Define a function to save the leaders per country dictionary in a JSON file
def save(leaders_per_country):
    # Import the json module
    import json
    # Open a file called leaders.json in write mode using a with statement
    with open("leaders.json", "w") as file:
        # Use json.dump to write the leaders per country dictionary to the file with indentation of 4 spaces
        json.dump(leaders_per_country, file, indent=4)

# Call the get_leaders function and assign its output to a variable called leaders_per_country
leaders_per_country = get_leaders()
# Call the save function with leaders_per_country as an argument
save(leaders_per_country)


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