import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pyshorteners
import time
import sys
import os
import json
import signal
import requests  # Don't forget to import the 'requests' library

# Function to print a moving loading message for a specific duration


def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


def print_moving_loading_message(duration_seconds):
    loader = ["|", "/", "-", "\\"]
    start_time = time.time()

    while time.time() - start_time < duration_seconds:
        for i in range(20):
            sys.stdout.write(
                "\rChecking for Fresh news... [loading " + loader[i % 4] + "]")
            sys.stdout.flush()
            time.sleep(0.1)

    # Clear the loading message
    sys.stdout.write("\r" + " " * 50)  # Clear the line
    sys.stdout.flush()

# Function to fetch and print article content from a shortened link


def fetch_and_print_article_content(shortened_link):
    try:
        response_article = requests.get(shortened_link)
        if response_article.status_code == 200:
            soup_article = BeautifulSoup(response_article.text, 'html.parser')

            # Extract the main text content of the article using BeautifulSoup
            article_content = ""
            for paragraph in soup_article.find_all('p'):
                article_content += paragraph.get_text() + "\n"

            slow_print("Article Content:")
            slow_print(article_content)
            print()
        else:
            slow_print(f'Failed to retrieve content for {shortened_link}')

    except requests.exceptions.RequestException as e:
        slow_print(f'Failed to retrieve content for {shortened_link}: {e}')

# Function to load cached articles from a file


def load_cached_articles():
    try:
        with open('cached_articles.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save articles to the cache file


def save_articles_to_cache(articles):
    with open('cached_articles.json', 'w') as file:
        json.dump(articles, file)

# Function to fetch news articles with search and filter


# Function to fetch news articles with search and filter
def fetch_new_news(search_words, num_minutes, keyword_filter=None):
    # Initialize a URL shortener
    s = pyshorteners.Shortener()

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, exit_gracefully)

    while True:
        # Load cached articles
        cached_articles = load_cached_articles()

        # Create a flag to check if new news has been found
        new_news_found = False
        # Initialize the start time before the while loop
        start_time = time.time()

        # Initialize a list to store the words used for searching
        used_search_words = []

        # Print a moving loading message for 5 seconds to indicate that the script is working
        print_moving_loading_message(duration_seconds=5)

        # Iterate through the search words
        for random_query in search_words:
            used_search_words.append(random_query)  # Add the word to the list

            # Replace this URL with the Google News API endpoint with the current query
            api_url = f'https://news.google.com/rss/search?q={random_query}&hl=en-US&gl=US&ceid=US:en'

            # Send an HTTP GET request to the Google News API endpoint
            response = requests.get(api_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the XML content of the RSS feed
                root = ET.fromstring(response.text)

                # Find and add articles posted in the last num_minutes minutes to the list
                for item in root.findall('.//item'):
                    # Check if the article has been cached
                    article_id = item.find('guid').text
                    if article_id in cached_articles:
                        continue  # Skip if already fetched

                    pub_date_str = item.find('pubDate').text
                    pub_date = datetime.strptime(
                        pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')

                    # Check if the article was posted within the last num_minutes minutes
                    if pub_date >= datetime.now() - timedelta(minutes=num_minutes):
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

                        # Print the new article
                        sys.stdout.write("\r" + " " * 50)  # Clear the line
                        sys.stdout.flush()
                        print("Words Used for Search: ", ', '.join(
                            used_search_words))  # Print used search words
                        print("Query: " + random_query)
                        print("Title: " + title)
                        print("Publication Date: " + pub_date_str)
                        print("Description: " + description_text)
                        print("Shortened Link: " + shortened_link)
                        print()

                        # Call the function to fetch and print article content
                        fetch_and_print_article_content(shortened_link)

                        # Add the new article to the cache
                        cached_articles.append(article_id)

                        # Set the flag to indicate that new news has been found
                        new_news_found = True

        # Save the updated cache
        save_articles_to_cache(cached_articles)

        # If no new news has been found for 5 seconds, display loading again
        if not new_news_found and time.time() - start_time >= 5:
            print_moving_loading_message(duration_seconds=5)

        # Wait for some time before checking for new news again (e.g., wait for 1 minute)
        time.sleep(10)  # 60 seconds = 1 minute


def slow_print(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)  # Adjust the sleep time to control the printing speed

# Function to handle a graceful exit


def exit_gracefully(signum, frame):
    print("\nExiting...")
    sys.exit(0)

# Main function to start listening for new news
# Main function to start listening for new news


# Main function to start listening for new news
def main():
    # Clear the console screen
    clear_screen()

    # Read search words from a file and store them in a list
    with open('words.txt', 'r') as file:
        search_words = [line.strip() for line in file]

    num_minutes = 300  # Fetch news posted in the last 5 minutes
    keyword_filter = input(
        "Enter a keyword to filter articles (or leave blank for no filter): ")

    # Start listening for new news
    fetch_new_news(search_words, num_minutes, keyword_filter)


if __name__ == "__main__":
    main()
