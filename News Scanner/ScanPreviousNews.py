import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pyshorteners
import time
import os
from colorama import Fore, Style

# Function to print text slowly

# Read words from a file and store them in a list
with open('words.txt', 'r') as file:
    search_words = [line.strip() for line in file]


def slow_print(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.05)
    print()  # Print a newline after the text

# Function to clear the console screen


def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

# Function to display a progress bar


def print_progress_bar(iteration, total, bar_length=50):
    percent = "{:.1%}".format(iteration / total)
    arrow = '=' * int(round(bar_length * iteration / total))
    spaces = ' ' * (bar_length - len(arrow))
    progress_bar = f"[{arrow + spaces}] {percent} Complete"
    print(progress_bar, end='\r', flush=True)

# Function to fetch news articles with search and filter


def get_crypto_fear_greed_index():
    # Replace this URL with the Crypto Fear & Greed Index API endpoint
    api_url = "https://api.alternative.me/fng/"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                return data['data'][0]['value']
            else:
                return "N/A"
        else:
            return "N/A"
    except requests.exceptions.RequestException as e:
        return "N/A"

# ... (previous code) ...

# Function to fetch news articles with search and filter


def fetch_articles(search_words, num_days, keyword_filter=None):
    # Initialize a URL shortener
    crypto_index = get_crypto_fear_greed_index()
    s = pyshorteners.Shortener()

    # Iterate through the search words
    for random_query in search_words:
        # Replace this URL with the Google News API endpoint with the current query
        api_url = f'https://news.google.com/rss/search?q={random_query}&hl=en-US&gl=US&ceid=US:en'

        # Send an HTTP GET request to the Google News API endpoint
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the XML content of the RSS feed
            root = ET.fromstring(response.text)

            # Get the current date and time
            current_datetime = datetime.now()

            # Calculate the start date based on the number of days
            start_date = current_datetime - timedelta(days=num_days)

            # Create a list to store articles for sorting
            articles = []

            # Find and add articles published in the specified number of days to the list
            for i, item in enumerate(root.findall('.//item')):
                pub_date_str = item.find('pubDate').text
                pub_date = datetime.strptime(
                    pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')

                # Check if the publication date is within the specified date range
                if pub_date >= start_date:
                    title = item.find('title').text
                    description_html = item.find('description').text
                    soup = BeautifulSoup(description_html, 'html.parser')
                    description_text = soup.get_text()
                    article_link = item.find('link').text

                    try:
                        # Shorten the article link with a custom timeout mechanism
                        shortened_link = s.tinyurl.short(article_link)
                    except requests.exceptions.RequestException as e:
                        # Handle request exceptions (including timeouts)
                        shortened_link = "URL Shortening Failed (Timeout or Error)"

                    # Apply keyword filter if provided
                    if keyword_filter and keyword_filter.lower() not in description_text.lower():
                        continue

                    # Append the article information to the list
                    articles.append({
                        'query': random_query,
                        'title': title,
                        'pub_date': pub_date_str,
                        'description': description_text,
                        'crypto_index': crypto_index,  # Add the Crypto Fear & Greed Index here
                        'shortened_link': shortened_link
                    })

                # Print a progress bar
                print_progress_bar(i + 1, len(root.findall('.//item')))

            # Sort the articles by publication date (newest to oldest)
            articles.sort(key=lambda x: datetime.strptime(
                x['pub_date'], '%a, %d %b %Y %H:%M:%S %Z'), reverse=True)

            # Print the filtered articles without pausing
            clear_screen()
            for article in articles:
                slow_print(Fore.YELLOW + "Query: " + article['query'])
                slow_print(Fore.CYAN + "Title: " + article['title'])
                slow_print(Fore.MAGENTA + "Publication Date: " +
                           article['pub_date'])
                slow_print(Fore.WHITE + "Description: " +
                           article['description'])
                slow_print(Fore.GREEN + "Crypto Fear & Greed Index: " +
                           str(article['crypto_index']))
                slow_print(Fore.BLUE + "Shortened Link: " +
                           article['shortened_link'])
                # Display the Crypto Fear & Greed Index
                print()

                # Open the shortened link and print its content
                try:
                    response_article = requests.get(article['shortened_link'])
                    if response_article.status_code == 200:
                        soup_article = BeautifulSoup(
                            response_article.text, 'html.parser')

                        # Extract the main text content of the article using BeautifulSoup
                        article_content = ""
                        for paragraph in soup_article.find_all('p'):
                            article_content += paragraph.get_text() + "\n"

                        slow_print(Fore.WHITE + "Article Content:")
                        slow_print(article_content)
                        print()
                    else:
                        slow_print(
                            f'Failed to retrieve content for {article["shortened_link"]}')

                except requests.exceptions.RequestException as e:
                    slow_print(
                        f'Failed to retrieve content for {article["shortened_link"]}: {e}')

# ... (previous code) ...

# Function to display news continuously without requiring user input


def print_news_continuously(articles):
    for article in articles:
        slow_print(Fore.YELLOW + "Query: " + article['query'])
        slow_print(Fore.CYAN + "Title: " + article['title'])
        slow_print(Fore.MAGENTA + "Publication Date: " + article['pub_date'])
        slow_print(Fore.WHITE + "Description: " + article['description'])
        slow_print(Fore.GREEN + "Crypto Fear & Greed Index: " +
                   str(article['crypto_index']))
        slow_print(Fore.BLUE + "Shortened Link: " + article['shortened_link'])
        print()

        # Add a short time delay (e.g., 2 seconds) before the next article
        time.sleep(2)

        # Open the shortened link and print its content
        try:
            response_article = requests.get(article['shortened_link'])
            if response_article.status_code == 200:
                soup_article = BeautifulSoup(
                    response_article.text, 'html.parser')

                # Extract the main text content of the article using BeautifulSoup
                article_content = ""
                for paragraph in soup_article.find_all('p'):
                    article_content += paragraph.get_text() + "\n"

                slow_print(Fore.WHITE + "Article Content:")
                slow_print(article_content)
                print()
            else:
                slow_print(
                    f'Failed to retrieve content for {article["shortened_link"]}')

        except requests.exceptions.RequestException as e:
            slow_print(
                f'Failed to retrieve content for {article["shortened_link"]}: {e}')

# ... (previous code) ...


# Main loop
while True:
    clear_screen()
    num_days = int(
        input(Fore.YELLOW + "Enter the number of days to scan for news (0 to exit): "))

    if num_days == 0:
        print("Exiting...")
        break

    keyword_filter = input(
        Fore.YELLOW + "Enter a keyword to filter articles (or leave blank for no filter): ")

    # Ask the user if they want to print continuously
    option = input(
        Fore.YELLOW + "Choose an option (1 for automatic, 2 for manual, 3 for continuous): ")

    if option == '1':
        # Automatic printing
        clear_screen()
        fetch_articles(search_words, num_days, keyword_filter)

    elif option == '2':
        # Manual printing (existing behavior)
        fetch_articles(search_words, num_days, keyword_filter)
        input("Press Enter to continue...")
