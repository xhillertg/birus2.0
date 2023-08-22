import requests
from bs4 import BeautifulSoup
import time

# URL of the Etherscan page listing the top Ethereum wallets
etherscan_url = "https://etherscan.io/accounts"

# User-Agent to mimic a web browser (change this to your preferred user-agent)
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"


def get_large_wallets(num_wallets_to_list):
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get(etherscan_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the table containing the wallet data
            wallet_table = soup.find("table", {"class": "table table-hover"})

            if wallet_table:
                rows = wallet_table.find_all("tr")[1:]  # Skip the header row
                wallets = []

                for row in rows:
                    columns = row.find_all("td")
                    if len(columns) >= 3:
                        rank = columns[0].text.strip()
                        address = columns[1].text.strip()
                        balance = columns[2].text.strip()

                        wallets.append((rank, address, balance))

                # Sort the wallets by balance in descending order
                sorted_wallets = sorted(wallets, key=lambda x: float(
                    x[2].replace(",", "")), reverse=True)

                # List the top N wallets
                for i, wallet in enumerate(sorted_wallets[:num_wallets_to_list]):
                    rank, address, balance = wallet
                    print(
                        f"Rank: {rank}, Address: {address}, Balance: {balance} ETH")

            else:
                print("Table not found on the Etherscan page.")

        else:
            print("Failed to fetch data from Etherscan.")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    num_wallets_to_list = 10  # Adjust the number of wallets to list as needed
    while True:
        get_large_wallets(num_wallets_to_list)
        # Add a delay between requests to avoid rate limiting (e.g., every 5 minutes)
        time.sleep(300)
