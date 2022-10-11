import requests
from bs4 import BeautifulSoup
import re

# USER DEFINED FUNCTIONS FOR WEB SCRAPING

# Web resources used: 
# - https://www.geeksforgeeks.org/web-scraping-amazon-customer-reviews/
# - https://gist.github.com/slowkow/7a7f61f495e3dbb7e3d767f97bd7304b

# Headers parameter for the GET request method
HEADERS = (
    {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 '
            'Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }
)


def get_data(url: str) -> str:
    """Makes a GET request to a given URL."""

    r = requests.get(url, headers=HEADERS)
    return r.text


def html_code(url: str) -> BeautifulSoup:
    """Renders the HTML for the given URL."""

    # Pass the url into get_data function
    htmldata = get_data(url)
    soup = BeautifulSoup(htmldata, 'html.parser')
    # Return html code
    return soup


def cus_rev(soup: BeautifulSoup) -> list:
    """Extract the customer reviews from the HTML."""

    # Find the html tag containing the reviews and convert into string
    data_str = ""

    for item in soup.find_all("div", class_="a-row a-spacing-small review-data"):
        data_str = data_str + item.get_text()

    result = data_str.split("\n")
    return result


def rev_date(soup: BeautifulSoup) -> list:
    """Extract the review dates from the HTML."""

    # Find the html tag containing the review date and convert into string
    date_str = ""
    date_list = []

    for item in soup.find_all("span", class_="a-size-base a-color-secondary review-date"):
        date_str = date_str + item.get_text()
        date_list.append(date_str)
        date_str = ""
    return date_list


def remove_emoji(string: str) -> str:
    """Remove emojis from text using regular expressions and returns a 'cleaned' string."""

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
